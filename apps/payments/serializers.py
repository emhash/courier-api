import stripe
from django.conf import settings
from rest_framework import serializers

from apps.orders.models import Order
from .models import Payment

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class CheckoutSessionSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    success_url = serializers.URLField(
        required=False, 
        default=f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/payment/success"
    )
    cancel_url = serializers.URLField(
        required=False, 
        default=f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')}/payment/cancel"
    )

    def validate_order_id(self, value):
        try:
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
            raise serializers.ValidationError('Order not found')
        
        request = self.context['request']
        if order.customer_id != request.user.id:
            raise serializers.ValidationError('You do not own this order')
        
        if hasattr(order, 'payment'):
            raise serializers.ValidationError('Payment already exists for this order')
        
        return value

    def create(self, validated_data):
        order = Order.objects.get(id=validated_data['order_id'])
        amount_cents = int(order.cost * 100)  # Convert to cents
        
        # Use FRONTEND_URL from settings
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')
        success_url = validated_data.get('success_url', f'{frontend_url}/payment/success')
        cancel_url = validated_data.get('cancel_url', f'{frontend_url}/payment/cancel')
        
        # Add order_id to cancel URL for better tracking
        if '?' not in cancel_url:
            cancel_url += f'?order_id={order.id}'
        else:
            cancel_url += f'&order_id={order.id}'

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Courier Order #{order.id}',
                            'description': order.description,
                        },
                        'unit_amount': amount_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=cancel_url,
                metadata={
                    'order_id': order.id,
                    'customer_id': order.customer_id
                }
            )
            
            # Create payment record with checkout session
            payment = Payment.objects.create(
                order=order,
                amount=order.cost,
                stripe_payment_intent_id=checkout_session.id,  # Store session ID temporarily
                status='PENDING',
            )
            
            return {
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'order_id': order.id,
                'amount': order.cost
            }

        except stripe.error.StripeError as e:
            raise serializers.ValidationError(f'Failed to create checkout session: {str(e)}') 