from django.urls import path
from .views import GenerateComplianceNoteAPIView,ComplianceNoteDetailUpdateDeleteAPIView, ComplianceNoteListCreateAPIView, SystemPromptListAPIView, SystemPromptPatchAPIView

urlpatterns = [
    path('', ComplianceNoteListCreateAPIView.as_view(), name='compliance-note-list-create'),
    path('<int:pk>', ComplianceNoteDetailUpdateDeleteAPIView.as_view(), name='compliance-detail-update-delete'),
    path('generate/', GenerateComplianceNoteAPIView.as_view(), name='generate-compliance-note'),
    path('system-prompt/', SystemPromptListAPIView.as_view(), name='system-prompt-list'),
    path('system-prompt/<int:pk>', SystemPromptPatchAPIView.as_view(), name='system-prompt-patch'),
]