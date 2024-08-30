from django.urls import path
from .views import (GenerateBrokerNoteAPIView, GeneratePdfView, BrokerNoteListCreateAPIView, BrokerNoteDetailUpdateDeleteAPIView)

urlpatterns = [
    path('', BrokerNoteListCreateAPIView.as_view(), name='broker-note-list-create'),
    path('<int:pk>', BrokerNoteDetailUpdateDeleteAPIView.as_view(), name='broker-note-detail-update-delete'),
    path('generate/', GenerateBrokerNoteAPIView.as_view(), name='generate-broker-note'),
    path('generate/pdf/', GeneratePdfView.as_view(), name='generate-broker-note-pdf'),
    
]