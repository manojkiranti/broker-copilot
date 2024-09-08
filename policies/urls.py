from django.urls import path
from .views import (BankPolicyListAPIView, BankPolicyNoteAPIView, BankListAPIView, PolicyListAPIView, ChatSessionListAPIView, MessageListAPIView)

urlpatterns = [
    path('', BankPolicyListAPIView.as_view(), name='bank-policy-list-create'),
    path('banks/', BankListAPIView.as_view(), name='bank-list-create'),
    path('policies/', PolicyListAPIView.as_view(), name='policy-list-create'),
    path('query/', BankPolicyNoteAPIView.as_view(), name='bank-policy-query'),
    path('chat-sessions/', ChatSessionListAPIView.as_view(), name='chat-sessions'),
    path('chat-sessions/<int:session_id>/messages/', MessageListAPIView.as_view(), name='chat-sessions-messages'),
]