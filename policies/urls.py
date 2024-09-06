from django.urls import path
from .views import (BankPolicyListAPIView, BankPolicyNoteAPIView, BankListAPIView, PolicyListAPIView)

urlpatterns = [
    path('', BankPolicyListAPIView.as_view(), name='bank-policy-list-create'),
    path('banks/', BankListAPIView.as_view(), name='bank-list-create'),
    path('policies/', PolicyListAPIView.as_view(), name='policy-list-create'),
    path('query/', BankPolicyNoteAPIView.as_view(), name='bank-policy-query'),
]