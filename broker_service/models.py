from django.db import models

# Create your models here.

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
    
