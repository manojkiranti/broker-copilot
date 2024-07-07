from django.urls import path
from .views import (
    UserLoginView,
    GenerateGoogleSignInLink,
    GoogleVerifyCodeForToken,
    GoogleVerifyAccessToken,
)

urlpatterns = [
    path('auth/login', UserLoginView.as_view(), name='user-login'),
    path('auth/google-redirect-link', GenerateGoogleSignInLink.as_view(), name='google-redirect-link'),
    path('auth/google-verify-token', GoogleVerifyCodeForToken.as_view(), name='google-verify-token'),
    path('auth/google-access-token', GoogleVerifyAccessToken.as_view(), name='google-access-token'),
]
