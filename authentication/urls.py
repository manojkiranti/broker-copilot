from django.urls import path
from .views import (
   UserLoginView, TwoFactorVerifyView, EnableTwoFactorView, VerifyTwoFactorView, DisableTwoFactorView
)

urlpatterns = [
    path('auth/v2/login', UserLoginView.as_view(), name='user-login-v2'),
    path('auth/verify-2fa/', TwoFactorVerifyView.as_view(), name='verify_2fa'),
    path('auth/enable-2fa/', EnableTwoFactorView.as_view(), name='enable_2fa'),
    path('auth/verify-enable-2fa/', VerifyTwoFactorView.as_view(), name='verify_enable_2fa'),
    path('auth/disable-2fa/', DisableTwoFactorView.as_view(), name='disable_2fa'),
]   
