from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class SystemPrompt(models.Model):
    loan_objectives = models.TextField(blank=True, null=True)
    loan_requirements = models.TextField(blank=True, null=True)
    loan_circumstances = models.TextField(blank=True, null=True)
    loan_financial_awareness = models.TextField(blank=True, null=True)
    loan_prioritised = models.TextField(blank=True, null=True)
    lender_loan = models.TextField(blank=True, null=True)
    loan_structure = models.TextField(blank=True, null=True)
    goals_objectives = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Compliance Note Systemprompt"