from django.urls import path
from .views import GeneratePdfView, OpportunityServiceListAPIView, OpportunityServiceCreateAPIView, OpportunityServiceDetailAPIView, OpportunityServiceUpdateAPIView
urlpatterns = [
    path('opportunity-service-history/all/', OpportunityServiceListAPIView.as_view(), name='opportunity-service-history-list'),
    path('opportunity-service-history/', OpportunityServiceCreateAPIView.as_view(), name='opportunity-service-history-create'),
    path('opportunity-service-history/update/<int:pk>', OpportunityServiceUpdateAPIView.as_view(), name='opportunity-service-history-update'),
    path('opportunity-service-history/<int:pk>', OpportunityServiceDetailAPIView.as_view(), name='opportunity-service-history-detail'),
     path('opportunity-service-history/generate-pdf/',
         GeneratePdfView.as_view(), name='opportunity-service-history-generate-pdf'),
]
