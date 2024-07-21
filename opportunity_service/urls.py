from django.urls import path
from .views import (
    OpportunityServiceListCreateAPIView, OpportunityServiceDetailUpdateDeleteAPIView, OpportunityServiceUpdateAPIView, 
    AllOpportunityServiceListAPIView, ContactListCreateUpdateAPIView)
urlpatterns = [
    path('opportunity-service-history/', OpportunityServiceListCreateAPIView.as_view(), name='opportunity-service-history-list-create'),
    path('opportunity-service-history/all/', AllOpportunityServiceListAPIView.as_view(), name='opportunity-service-history-list-users'),
    path('opportunity-service-history/update/<int:pk>', OpportunityServiceUpdateAPIView.as_view(), name='opportunity-service-history-update'),
    path('opportunity-service-history/<int:pk>', OpportunityServiceDetailUpdateDeleteAPIView.as_view(), name='opportunity-service-history-detail-delete'),
    path('opportunity-service-history/contact/', ContactListCreateUpdateAPIView.as_view(), name='opportunity-contact-list-create-update'),
]