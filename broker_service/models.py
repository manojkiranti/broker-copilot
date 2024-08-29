from django.db import models
from django.contrib.auth import get_user_model
from opportunity_app.models import Opportunity
from utils.constant import StatusChoices
User = get_user_model()

class SystemPrompt(models.Model):
    loan_purpose = models.TextField(blank=True, null=True)
    applicant_overview = models.TextField(blank=True, null=True)
    living_condition = models.TextField(blank=True, null=True)
    employment_income = models.TextField(blank=True, null=True)
    commitments = models.TextField(blank=True, null=True)
    others = models.TextField(blank=True, null=True)
    mitigants = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Broker Note Systemprompt"
    
class Note(models.Model):
    loan_details = models.JSONField(default=dict)
    funds_available = models.JSONField(default=dict)
    funds_complete = models.JSONField(default=dict)
    
    loan_purpose_note = models.TextField(blank=True, null=True)
    applicant_overview_note = models.TextField(blank=True, null=True)
    living_condition_note = models.TextField(blank=True, null=True)
    employment_income_note = models.TextField(blank=True, null=True)
    commitments_note = models.TextField(blank=True, null=True)
    other_note = models.TextField(blank=True, null=True)
    mitigants_note = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, related_name="broker_opportunities")
     
    created_by = models.ForeignKey(User, related_name='created_broker_note', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='updated_broker_note', on_delete=models.SET_NULL, null=True)
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class NotePdf(models.Model):
    note = models.ForeignKey(Note, related_name="pdfs", on_delete=models.CASCADE)
    pdf_url = models.URLField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"PDF for Note {self.note.id}"