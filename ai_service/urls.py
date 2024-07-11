from django.urls import path, include

from ai_service.views import getAISettings, getAIAccountInfo, FeedbackAPIView

urlpatterns = [
    path('auth_setup/', getAISettings.as_view(), name="ai_settings"),
    path('.auth/me/', getAIAccountInfo.as_view(), name="ai_users"),
    path('feedback/', FeedbackAPIView.as_view(), name="ai_feedback"),
]
