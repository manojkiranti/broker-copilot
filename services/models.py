from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model

User = get_user_model()

class Service(models.Model):
    name = models.CharField(max_length=255)
    url=models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class BrokerServiceStatus(Enum):
    IN_PROGRESS = 'progress'
    COMPLETED = 'completed'
    FAILED = 'failed'

    def __str__(self):
        return self.value

class BrokerServiceHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in BrokerServiceStatus], default=BrokerServiceStatus.IN_PROGRESS.value)
    website_tracking_id = models.CharField(max_length=255)
    json_data = models.JSONField(default=dict)
    api_request = models.JSONField(default=dict)
    api_response = models.JSONField(default=dict)
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.service.name} - {self.status} - {self.website_tracking_id}"

class ContactInfo(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    citizenship_number = models.CharField(max_length=99, null=True, blank=True)

    def __str__(self):
        return self.name