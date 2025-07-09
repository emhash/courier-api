from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.payments.views import PaymentSuccessView, PaymentCancelView

urlpatterns = [
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='homepage'),
    path('admin/', admin.site.urls),

    # APIs ==>
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Payment redirect pages  ==>
    path('payment/success/', PaymentSuccessView.as_view(), name='payment-success-page'),
    path('payment/cancel/', PaymentCancelView.as_view(), name='payment-cancel-page'),
]
