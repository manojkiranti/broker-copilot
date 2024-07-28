from rest_framework import serializers
from .models import  ContactsOpportunity, Opportunity
from django.contrib.auth import get_user_model
User = get_user_model()
    
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactsOpportunity
        fields = ['id', 'name', 'email', 'phone', 'residency', 'citizenship']
        read_only_fields = ['created_at', 'updated_at']
        

class ContactDataSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, allow_null=True, allow_blank=True, required=False)
    email = serializers.EmailField(required=True)  # Email is required
    phone = serializers.CharField(max_length=15, allow_null=True, allow_blank=True, required=False)
    citizenship =  serializers.CharField(max_length=100, allow_null=True, allow_blank=True, required=False)
    residency = serializers.CharField(max_length=99, allow_null=True, allow_blank=True, required=False)
    country_code =serializers.CharField(max_length=10, allow_null=True, allow_blank=True, required=False)
    
class OpportunitySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    type = serializers.ChoiceField(choices=Opportunity.OpportunityType.choices)
    website_tracking_id = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    json_data = serializers.JSONField(default=dict)
   
    primary_contact = ContactDataSerializer(required=False)
    secondary_contact = ContactDataSerializer(required=False)
    other_contact = ContactDataSerializer(required=False)
    
    primary_processor = serializers.CharField(max_length=150, required=False, allow_blank=True)
    secondary_processor = serializers.CharField(max_length=150, required=False, allow_blank=True)
    
    start_date = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(allow_null=True, required=False)

    def validate_website_tracking_id(self, value):
        if value == '':
            return None
        return value
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'json_data' in ret and isinstance(instance.json_data, dict):
            ret['json_data']['id'] = instance.id
        # ret['primary_contact'] = ContactSerializer(instance.primary_contact).data if instance.primary_contact else None
        # ret['secondary_contacts'] = ContactSerializer(instance.secondary_contacts.all(), many=True).data
        return ret




class GeneratePdfSerializer(serializers.Serializer):
    json_data = serializers.JSONField()
