from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.views.generic import TemplateView
import stripe

from .serializers import CheckoutSessionSerializer
from .models import Payment
from apps.orders.models import Order

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class CheckoutSessionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSessionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        checkout_data = serializer.save()
        
        response_data = checkout_data.copy()
        response_data["message"] = "Checkout session created successfully. Redirect user to checkout_url"
        return Response(response_data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=session['id'])
                payment.status = 'SUCCEEDED'
                payment.stripe_payment_intent_id = session.get('payment_intent', session['id'])
                payment.save()
                print(f"✅ Payment {payment.id} marked as SUCCEEDED for order {payment.order.id}")
                
            except Payment.DoesNotExist:
                print(f"❌ Payment not found for session {session['id']}")

        # Handle checkout session expired event
        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=session['id'])
                payment.status = 'FAILED'
                payment.save()
                print(f"⏰ Payment {payment.id} marked as FAILED (session expired) for order {payment.order.id}")
                
            except Payment.DoesNotExist:
                print(f"❌ Payment not found for expired session {session['id']}")

        # Handle payment intent succeeded (backup confirmation)
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
                if payment.status != 'SUCCEEDED':
                    payment.status = 'SUCCEEDED'
                    payment.save()
                    print(f"✅ Payment {payment.id} confirmed as SUCCEEDED (payment_intent) for order {payment.order.id}")
                    
            except Payment.DoesNotExist:
                print(f"❌ Payment not found for payment_intent {payment_intent['id']}")

        # Handle payment intent failed
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            
            try:
                payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
                payment.status = 'FAILED'
                payment.save()
                print(f"❌ Payment {payment.id} marked as FAILED for order {payment.order.id}")
                
            except Payment.DoesNotExist:
                print(f"❌ Payment not found for failed payment_intent {payment_intent['id']}")

        else:
            print(f"ℹ️ Unhandled event type: {event['type']}")

        return HttpResponse(status=200)


class PaymentSuccessView(TemplateView):
    template_name = 'payment/success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session_id'] = self.request.GET.get('session_id', '')
        return context


class PaymentCancelView(TemplateView):
    template_name = 'payment/cancel.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_id'] = self.request.GET.get('order_id', '')
        return context


class RetryPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, payment_id):
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.order.customer_id != request.user.id:
            return Response(
                {"error": "You do not own this payment"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if payment can be retried
        if payment.status == 'SUCCEEDED':
            return Response(
                {"error": "Payment already succeeded. Cannot retry."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount_cents = int(payment.amount * 100)
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Courier Order #{payment.order.id} (Retry)',
                            'description': payment.order.description,
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{frontend_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{frontend_url}/payment/cancel?order_id={payment.order.id}',
                metadata={
                    'order_id': payment.order.id,
                    'customer_id': payment.order.customer_id,
                    'retry_payment_id': payment.id
                }
            )
            
            payment.stripe_payment_intent_id = checkout_session.id
            payment.status = 'PENDING'
            payment.save()
            
            return Response({
                'message': 'Payment retry session created successfully. Redirect user to checkout_url',
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'payment_id': payment.id,
                'order_id': payment.order.id,
                'amount': payment.amount
            }, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Failed to create retry checkout session: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            ) 