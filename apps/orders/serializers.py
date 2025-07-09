from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order

User = get_user_model()


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
    class Meta:
        model = Order
        fields = ['description', 'address', 'cost']

    def create(self, validated_data):
        # Simple order creation - payment handled separately
        order = Order.objects.create(**validated_data)
        return order 