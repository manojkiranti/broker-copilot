from django.urls import path
from .views import (GenerateBrokerNoteAPIView)

urlpatterns = [
    path('generate/', GenerateBrokerNoteAPIView.as_view(), name='generate-broker-note')
]