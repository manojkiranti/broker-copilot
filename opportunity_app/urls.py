from django.urls import path
from .views import (
    OpportunityListCreateAPIView, OpportunityServiceDetailUpdateDeleteAPIView, 
    AllOpportunityServiceListAPIView, ContactListCreateUpdateAPIView,
    ContactDetailUpdateAPIView
    )
urlpatterns = [
    path('opportunity/', OpportunityListCreateAPIView.as_view(), name='opportunity-list-create'),
    path('opportunity/all/', AllOpportunityServiceListAPIView.as_view(), name='opportunity-list-all-users'),
    path('opportunity/<int:pk>', OpportunityServiceDetailUpdateDeleteAPIView.as_view(), name='opportunity-detail-update-delete'),
    path('opportunity/contact/', ContactListCreateUpdateAPIView.as_view(), name='opportunity-contact-list-create-update'),
    path('opportunity/contact/<int:pk>', ContactDetailUpdateAPIView.as_view(), name='opportunity-contact-create-update'),
]