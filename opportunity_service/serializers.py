from rest_framework import serializers
from .models import  ContactsOpportunity, OpportunityService
from django.contrib.auth import get_user_model
User = get_user_model()
from enum import Enum

class OpportunityServiceType(Enum):
    PURCHASE = 'purchase'
    REFINANCE = 'refinance'
    
    
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsOpportunity
        fields = ['name', 'email', 'phone', 'residency', 'created_by', 'updated_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']
        
        
class OpportunityServiceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=[(tag.value, tag.name) for tag in OpportunityServiceType])
    website_tracking_id = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    json_data = serializers.JSONField(required=False)
    api_request = serializers.JSONField(required=False)
    api_response = serializers.JSONField(required=False)
    user_contact_name = serializers.CharField(max_length=255, required=False)
    user_contact_email = serializers.EmailField(max_length=99, required=False)
    user_contact_phone = serializers.CharField(max_length=99, required=False)
    user_contact_identity_number = serializers.CharField(max_length=255, required=False)
    primary_contact = serializers.CharField(required=False)
    secondary_contact =  serializers.CharField(required=False)
    user_contact = ContactSerializer(read_only=True)
    
    def validate_website_tracking_id(self, value):
        """
        Convert empty string to None for website_tracking_id to handle unique constraint with null values.
        """
        if value == '':
            return None
        return value
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        
        # Add 'id' inside 'json_data' if it exists
        if 'json_data' in ret and isinstance(ret['json_data'], dict):
            ret['json_data']['id'] = instance.id
        
        return ret
    

class GeneratePdfSerializer(serializers.Serializer):
    json_data = serializers.JSONField()
