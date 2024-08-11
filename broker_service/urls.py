from django.urls import path
from .views import (GenerateBrokerNoteAPIView, GeneratePdfView)

urlpatterns = [
    path('generate/', GenerateBrokerNoteAPIView.as_view(), name='generate-broker-note'),
    path('generate/pdf/', GeneratePdfView.as_view(), name='generate-broker-note-pdf')
]