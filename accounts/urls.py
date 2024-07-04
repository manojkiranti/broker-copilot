from django.urls import path
from . import views  

urlpatterns = [
    path('auth/login/', views.OAuthUserLoginAPIView.as_view(), name='oauth-user-login'),
]
