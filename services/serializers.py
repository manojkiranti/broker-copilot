from rest_framework import serializers
from .models import BrokerServiceHistory, ContactInfo

class BrokerServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrokerServiceHistory
        fields = ('id', 'website_tracking_id', 'service', 'status', 'json_data', 'api_request', 'api_response', )

class BrokerServiceHistorySerializer(serializers.Serializer):
    website_tracking_id = serializers.CharField(max_length=255)
    json_data = serializers.JSONField()
    api_request = serializers.JSONField(required=False)
    api_response = serializers.JSONField(required=False)


class BrokerServiceHistoryUpdateSerializer(serializers.Serializer):
    json_data = serializers.JSONField()
    api_request = serializers.JSONField(required=False)
    api_response = serializers.JSONField(required=False)


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['name', 'email', 'phone', 'citizenship_number']