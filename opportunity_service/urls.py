from django.urls import path
from .views import OpportunityServiceListAPIView, OpportunityServiceCreateAPIView, OpportunityServiceDetailAPIView
urlpatterns = [
    path('opportunity-service-history/all/', OpportunityServiceListAPIView.as_view(), name='opportunity-service-history-list'),
    path('opportunity-service-history/', OpportunityServiceCreateAPIView.as_view(), name='opportunity-service-history-create'),
    path('opportunity-service-history/<int:pk>', OpportunityServiceDetailAPIView.as_view(), name='opportunity-service-history-detail'),
]