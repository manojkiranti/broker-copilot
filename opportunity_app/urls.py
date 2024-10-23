from django.urls import path
from .views import (
    OpportunityListCreateAPIView, OpportunityServiceDetailUpdateDeleteAPIView,  OpportunityServiceDetailUpdateAPIView,
    AllOpportunityServiceListAPIView, ContactListCreateUpdateAPIView,
    ContactDetailUpdateAPIView, ContactCheckAPIView
    )
urlpatterns = [
    path('opportunity/', OpportunityListCreateAPIView.as_view(), name='opportunity-list-create'),
   
    path('opportunity/all/', AllOpportunityServiceListAPIView.as_view(), name='opportunity-list-all-users'),
    path('opportunity/<int:pk>', OpportunityServiceDetailUpdateDeleteAPIView.as_view(), name='opportunity-detail-update-delete'),
    path('v2/opportunity/<int:pk>', OpportunityServiceDetailUpdateAPIView.as_view(), name='opportunity-detail-v2'),
    path('opportunity/contact/', ContactListCreateUpdateAPIView.as_view(), name='opportunity-contact-list-create-update'),
    path('opportunity/contact/<int:pk>', ContactDetailUpdateAPIView.as_view(), name='opportunity-contact-create-update'),
    path('opportunity/contact/create-or-retrieve/', ContactCheckAPIView.as_view(), name='opportunity-contact-create-or-retrieve'),
]