from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from .models import  ContactsOpportunity, Opportunity
from accounts.serializers import UserListSerializer
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

class OpportunityNameSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    
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
    stage = serializers.SlugRelatedField(read_only=True, slug_field='name')
    
    created_by = UserListSerializer(read_only=True)  

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.website_tracking_id = validated_data.get('website_tracking_id', instance.website_tracking_id)
        instance.json_data = validated_data.get('json_data', instance.json_data)
        
        # Handle contacts
        primary_contact_data = validated_data.get('primary_contact', None)
        if primary_contact_data:
            primary_contact, created = ContactsOpportunity.objects.get_or_create(
                email=primary_contact_data['email'],
                defaults=primary_contact_data
            )
            if not created:
                for key, value in primary_contact_data.items():
                    if key != 'email':
                        setattr(primary_contact, key, value)
                primary_contact.save()
            instance.primary_contact = primary_contact
        
        secondary_contact_data = validated_data.get('secondary_contact', None)
        if secondary_contact_data:
            secondary_contact, created = ContactsOpportunity.objects.get_or_create(
                email=secondary_contact_data['email'],
                defaults=secondary_contact_data
            )
            if not created:
                for key, value in secondary_contact_data.items():
                    if key != 'email':
                        setattr(secondary_contact, key, value)
                secondary_contact.save()
            instance.secondary_contact = secondary_contact

        # Handle processors
        primary_processor_email = validated_data.get('primary_processor', None)
        if primary_processor_email:
            instance.primary_processor = User.objects.get(email=primary_processor_email)
        
        secondary_processor_email = validated_data.get('secondary_processor', None)
        if secondary_processor_email:
            instance.secondary_processor = User.objects.get(email=secondary_processor_email)
        
        instance.save()
        return instance
    
    def validate_website_tracking_id(self, value):
        if value == '':
            return None
        return value
    
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        print(ret)
        if 'json_data' in ret and isinstance(instance.json_data, dict):
            ret['json_data']['id'] = instance.id
        # ret['primary_contact'] = ContactSerializer(instance.primary_contact).data if instance.primary_contact else None
        # ret['secondary_contacts'] = ContactSerializer(instance.secondary_contacts.all(), many=True).data
        if 'primary_processor' in ret:
            try:
                user = User.objects.get(email=ret['primary_processor'])
                ret['primary_processor'] = UserListSerializer(user).data
            except ObjectDoesNotExist:
                ret['primary_processor'] = None
        if 'secondary_processor' in ret:
            try:
                user = User.objects.get(email=ret['secondary_processor'])
                ret['secondary_processor'] = UserListSerializer(user).data
            except ObjectDoesNotExist:
                ret['secondary_processor'] = None
        return ret




class GeneratePdfSerializer(serializers.Serializer):
    json_data = serializers.JSONField()
