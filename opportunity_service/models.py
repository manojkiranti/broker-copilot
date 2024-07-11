from django.db import models
from enum import Enum
from django.contrib.auth import get_user_model

from services.models import Service

User = get_user_model()

class OpportunityServiceStatus(Enum):
    IN_PROGRESS = 'progress'
    COMPLETED = 'completed'
    FAILED = 'failed'

    def __str__(self):
        return self.value

class OpportunityService(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service")
    status = models.CharField(max_length=20, choices=[(tag.value, tag.name) for tag in OpportunityServiceStatus], default=OpportunityServiceStatus.IN_PROGRESS.value)
    website_tracking_id = models.CharField(max_length=255, null=True)
    json_data = models.JSONField(default=dict)
    api_request = models.JSONField(default=dict)
    api_response = models.JSONField(default=dict)
    start_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.service.name} - {self.status}"
