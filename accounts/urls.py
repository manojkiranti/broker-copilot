from django.urls import path
from .views import (
    UserLoginView,
    UserRegisterView,
    GenerateGoogleSignInLink,
    GoogleVerifyCodeForToken,
    GoogleVerifyAccessToken,
    UserListCreateAPIView,
    UserFeedbackCreateAPIView,
    UserUpdateAPIView,
    UserDetailAPIView
)

urlpatterns = [
    path('auth/login', UserLoginView.as_view(), name='user-login'),
    path('auth/register', UserRegisterView.as_view(), name='user-register'),
    path('auth/google-redirect-link', GenerateGoogleSignInLink.as_view(), name='google-redirect-link'),
    path('auth/google-verify-token', GoogleVerifyCodeForToken.as_view(), name='google-verify-token'),
    path('auth/google-access-token', GoogleVerifyAccessToken.as_view(), name='google-access-token'),
    path('auth/users', UserListCreateAPIView.as_view(), name='users-list-create'),
    path('auth/feedback', UserFeedbackCreateAPIView.as_view(), name='user-feedback'),
    path('user/update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('user/me/', UserDetailAPIView.as_view(), name='user-detail'),
]   
