from rest_framework import serializers
from .models import  ContactsOpportunity, Opportunity
from django.contrib.auth import get_user_model
User = get_user_model()
from enum import Enum

class OpportunityType(Enum):
    PURCHASE = 'purchase'
    REFINANCE = 'refinance'
    
    
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsOpportunity
        fields = ['name', 'email', 'phone', 'residency']
        read_only_fields = ['created_at', 'updated_at']
        

class OpportunitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=[(tag.value, tag.name) for tag in OpportunityType])
    website_tracking_id = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    json_data = serializers.JSONField(default=dict)
    api_request = serializers.JSONField(default=dict)
    api_response = serializers.JSONField(default=dict)
    user_contact = ContactSerializer(read_only=True)
    primary_contact = serializers.CharField(max_length=150, required=False, allow_blank=True)
    secondary_contact = serializers.CharField(max_length=150, required=False, allow_blank=True)
    created_by = serializers.CharField(max_length=150, required=False, allow_blank=True)
    updated_by = serializers.CharField(max_length=150, required=False, allow_blank=True)
    start_date = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(allow_null=True, required=False)
    
    user_contact_name = serializers.CharField(max_length=255, required=False)
    user_contact_email = serializers.EmailField(max_length=99, required=False)
    user_contact_phone = serializers.CharField(max_length=15, required=False)
    user_contact_residency = serializers.CharField(max_length=255, required=False)

    def validate_website_tracking_id(self, value):
        if value == '':
            return None
        return value

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'json_data' in ret and isinstance(instance.json_data, dict):
            ret['json_data']['id'] = instance.id
        return ret




class GeneratePdfSerializer(serializers.Serializer):
    json_data = serializers.JSONField()
