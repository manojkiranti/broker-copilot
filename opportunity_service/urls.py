from django.urls import path
from .views import OpportunityServiceListAPIView, OpportunityServiceCreateAPIView, OpportunityServiceDetailUpdateDeleteAPIView, OpportunityServiceUpdateAPIView, AllOpportunityServiceListAPIView
urlpatterns = [
    path('opportunity-service-history/all/', OpportunityServiceListAPIView.as_view(), name='opportunity-service-history-list'),
    path('opportunity-service-history/all/users/', AllOpportunityServiceListAPIView.as_view(), name='opportunity-service-history-list-users'),
    path('opportunity-service-history/', OpportunityServiceCreateAPIView.as_view(), name='opportunity-service-history-create'),
    path('opportunity-service-history/update/<int:pk>', OpportunityServiceUpdateAPIView.as_view(), name='opportunity-service-history-update'),
    path('opportunity-service-history/<int:pk>', OpportunityServiceDetailUpdateDeleteAPIView.as_view(), name='opportunity-service-history-detail'),
]