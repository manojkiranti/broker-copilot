from django.urls import path
from . import views  

urlpatterns = [
    path('auth/login', views.OAuthUserLoginAPIView.as_view(), name='oauth-user-login'),
    path('auth/google-redirect-link', views.GenerateGoogleSignInLink.as_view(), name='google-redirect-link'),
    path('auth/google-verify-token', views.GoogleVerifyCodeForToken.as_view(), name='google-verify-token'),
]
