from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
import stripe
from .models import Order

User = get_user_model()
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.ReadOnlyField(source='customer.username')
    delivery_man = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.filter(role='delivery_man'),
        required=False,
        allow_null=True,
    )
    payment_status = serializers.SerializerMethodField()
    has_payment = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'customer')

    def get_payment_status(self, obj):
        if hasattr(obj, 'payment'):
            return obj.payment.status
        return None

    def get_has_payment(self, obj):
        return hasattr(obj, 'payment')


class OrderCreateSerializer(serializers.ModelSerializer):
    create_payment = serializers.BooleanField(default=False, write_only=True)
    success_url = serializers.URLField(required=False, write_only=True)
    cancel_url = serializers.URLField(required=False, write_only=True)
    
    class Meta:
        model = Order
        fields = ['description', 'address', 'cost', 'create_payment', 'success_url', 'cancel_url']

    def create(self, validated_data):
        # Extract payment-related fields
        create_payment = validated_data.pop('create_payment', False)
        success_url = validated_data.pop('success_url', None)
        cancel_url = validated_data.pop('cancel_url', None)
        
        order = Order.objects.create(**validated_data)
        
        # If payment requested--> create checkout session==>>
        if create_payment:
            try:
                from apps.payments.models import Payment
                
                amount_cents = int(order.cost * 100)  # Convert to cents
                frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')
                
                if not success_url:
                    success_url = f'{frontend_url}/payment/success'
                if not cancel_url:
                    cancel_url = f'{frontend_url}/payment/cancel'
                
                #  order_id to cancel URL for better tracking
                if '?' not in cancel_url:
                    cancel_url += f'?order_id={order.id}'
                else:
                    cancel_url += f'&order_id={order.id}'

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
                
                Payment.objects.create(
                    order=order,
                    amount=order.cost,
                    stripe_payment_intent_id=checkout_session.id,
                    status='PENDING',
                )
                
                order.checkout_url = checkout_session.url
                order.session_id = checkout_session.id
                
            except stripe.error.StripeError as e:
                order.delete()
                raise serializers.ValidationError(f'Failed to create payment session: {str(e)}')
        
        return order 