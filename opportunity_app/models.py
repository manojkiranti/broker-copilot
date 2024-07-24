from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model

User = get_user_model()


class ContactsOpportunity(models.Model):
    class OpportunityStatus(models.TextChoices):
        ACTIVE  = 'active', 'Active',
        INACTIVE = 'inactive', 'Inactive'
    
        
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    residency = models.CharField(max_length=99, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=OpportunityStatus.choices, default=OpportunityStatus.ACTIVE)
    
    created_by = models.ForeignKey(User, related_name='created_contacts', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='updated_contacts', on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.email
    
class Opportunity(models.Model):
    class OpportunityType(models.TextChoices):
        PURCHASE = 'purchase', 'Purchase'
        REFINANCE = 'refinance', 'Refinance'

    class OpportunityStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        
    class OpportunityStage(models.TextChoices):
        ENGAGED = 'engaged', 'Engaged'
        SUCCESS = 'success', 'Success'
        UNSUCCESSFUL = 'unsuccessful', 'Unsuccessful'
        IDEAL = 'ideal', 'Ideal'
        
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=20, choices=OpportunityType.choices)
    status = models.CharField(max_length=20, choices=OpportunityStatus.choices, default=OpportunityStatus.ACTIVE)
    stage = models.CharField(max_length=20, choices=OpportunityStage.choices, default=OpportunityStage.ENGAGED)
    
    website_tracking_id = models.CharField(unique=True, max_length=255, null=True)
    json_data = models.JSONField(default=dict)

    primary_contact = models.ForeignKey(ContactsOpportunity, on_delete=models.SET_NULL, null=True, related_name="primary_opportunities")
    secondary_contact = models.ForeignKey(ContactsOpportunity, on_delete=models.SET_NULL, null=True, related_name="secondary_opportunities")
    other_contact = models.ForeignKey(ContactsOpportunity, on_delete=models.SET_NULL, null=True, related_name="other_opportunities")
   
    primary_processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name="primary_processor_opportunity")
    secondary_processor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name="secondary_processor_opportunity")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_opportunity")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="updated_opportunity")
    
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.status} - {self.name}"

