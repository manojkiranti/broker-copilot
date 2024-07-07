from rest_framework import serializers
from .models import BrokerServiceHistoryDetail

class BrokerServiceHistoryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerServiceHistoryDetail
        fields = ['website_tracking_id', 'broker_service_history', 'json_data', 'start_date', 'api_request', 'api_response']
