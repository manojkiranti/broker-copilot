from django.urls import path
from .views import GenerateComplianceNoteAPIView, ComplianceNoteListCreateAPIView

urlpatterns = [
    path('', ComplianceNoteListCreateAPIView.as_view(), name='compliance-note-list-create'),
    path('generate/', GenerateComplianceNoteAPIView.as_view(), name='generate-compliance-note')
]