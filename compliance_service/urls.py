from django.urls import path
from .views import GenerateComplianceNoteAPIView
urlpatterns = [
    path('generate/', GenerateComplianceNoteAPIView.as_view(), name='generate-compliance-note')
]