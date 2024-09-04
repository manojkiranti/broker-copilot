from django.urls import path
from .views import (GenerateBrokerNoteAPIView, GeneratePdfView, BrokerNoteListCreateAPIView, BrokerNoteDetailUpdateDeleteAPIView, GenerateBrokerNoteV2APIView, SystemPromptListAPIView, SystemPromptPatchAPIView)

urlpatterns = [
    path('', BrokerNoteListCreateAPIView.as_view(), name='broker-note-list-create'),
    path('<int:pk>', BrokerNoteDetailUpdateDeleteAPIView.as_view(), name='broker-note-detail-update-delete'),
    path('generate/', GenerateBrokerNoteAPIView.as_view(), name='generate-broker-note'),
    path('v2/generate/', GenerateBrokerNoteV2APIView.as_view(), name='generate-broker-note-v2'),
    path('generate/pdf/', GeneratePdfView.as_view(), name='generate-broker-note-pdf'),
    path('system-prompt/', SystemPromptListAPIView.as_view(), name='broker-note-system-prompt-list'),
    path('system-prompt/<int:pk>', SystemPromptPatchAPIView.as_view(), name='broker-note-system-prompt-patch'),
    
]