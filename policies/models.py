from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Bank(models.Model):
    name = models.CharField(max_length=255)
    operating_country = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name

class Policy(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name

class BankPolicy(models.Model):
    bank = models.ForeignKey(Bank, related_name='bank_policies', on_delete=models.CASCADE)
    policy = models.ForeignKey(Policy, related_name='bank_policies', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True) 
    created_by = models.ForeignKey(User, related_name='bank_policy_created_by', on_delete=models.SET_NULL, null=True)
    updated_by = models.ForeignKey(User, related_name='bank_policy_updated_by', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.bank} - {self.policy}"