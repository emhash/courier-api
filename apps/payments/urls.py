from django.urls import path
from .views import (
    CheckoutSessionView,
    StripeWebhookView,
    PaymentSuccessView,
    PaymentCancelView,
    RetryPaymentView
)

urlpatterns = [
    # Stripe Checkout Session (hosted checkout) - MAIN PAYMENT ENDPOINT
    path('checkout/', CheckoutSessionView.as_view(), name='checkout-session'),
    
    # Retry payment for pending/failed payments
    path('retry/<int:payment_id>/', RetryPaymentView.as_view(), name='retry-payment'),
    
    # Webhooks - Handle payment completion
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # Success and Cancel pages
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
] 