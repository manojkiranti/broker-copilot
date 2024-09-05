from django.urls import path
from .views import (BankPolicyListAPIView)

urlpatterns = [
    path('', BankPolicyListAPIView.as_view(), name='bank-policy-list-create'),
]