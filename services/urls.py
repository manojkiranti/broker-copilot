from django.urls import path
from .views import BrokerServiceHistoryCreateAPIView, BrokerServiceHistoryUpdateAPIView, BrokerServiceHistoryListAPIView, BrokerServiceHistoryRetrieveAPIView

urlpatterns = [
    path('broker-service-history/all/', BrokerServiceHistoryListAPIView.as_view(), name='broker-service-history-list'),
    path('broker-service-history/', BrokerServiceHistoryCreateAPIView.as_view(), name='broker-service-history-create'),
    path('broker-service-history/<int:pk>/', BrokerServiceHistoryUpdateAPIView.as_view(), name='broker-service-history-update'),
    path('broker-service-retrieve/<int:pk>/', BrokerServiceHistoryRetrieveAPIView.as_view(), name='broker-service-history-retrieve'),
]