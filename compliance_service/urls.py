from django.urls import path
from .views import GenerateComplianceNoteAPIView,ComplianceNoteDetailUpdateDeleteAPIView, ComplianceNoteListCreateAPIView

urlpatterns = [
    path('', ComplianceNoteListCreateAPIView.as_view(), name='compliance-note-list-create'),
    path('<int:pk>', ComplianceNoteDetailUpdateDeleteAPIView.as_view(), name='compliance-detail-update-delete'),
    path('generate/', GenerateComplianceNoteAPIView.as_view(), name='generate-compliance-note')
]