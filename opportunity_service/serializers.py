from rest_framework import serializers
from .models import OpportunityService


class OpportunityServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    website_tracking_id = serializers.CharField(max_length=255, required=False)
    json_data = serializers.JSONField()
    api_request = serializers.JSONField(required=False)
    api_response = serializers.JSONField(required=False)
    
    def to_representation(self, instance):
        # Serialize the original data first
        ret = super().to_representation(instance)

        # Add 'id' inside 'json_data' if it exists
        if 'json_data' in ret and isinstance(ret['json_data'], dict):
            ret['json_data']['id'] = instance.id
        
        return ret