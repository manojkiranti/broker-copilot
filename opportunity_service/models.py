from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model

User = get_user_model()

class OpportunityServiceStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

    def __str__(self):
        return self.value

class ContactsOpportunity(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    identity_number = models.CharField(max_length=99, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class OpportunityService(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="opportunity_services")
    status = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in OpportunityServiceStatus], default=OpportunityServiceStatus.ACTIVE.value)
    website_tracking_id = models.CharField(max_length=255, null=True)
    json_data = models.JSONField(default=dict)
    api_request = models.JSONField(default=dict)
    api_response = models.JSONField(default=dict)
    user_contact = models.ForeignKey(ContactsOpportunity, on_delete=models.CASCADE, related_name="contact_opportunity_services", null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.status}"

