from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class BrokerServiceHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    start_date = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.service.name} - {self.status}"

class BrokerServiceHistoryDetail(models.Model):
    website_tracking_id = models.CharField(max_length=255)
    broker_service_history = models.ForeignKey(BrokerServiceHistory, on_delete=models.CASCADE)
    json_data = models.JSONField()
    start_date = models.DateTimeField(auto_now_add=True)
    api_request = models.JSONField()
    api_response = models.JSONField()

    def __str__(self):
        return f"Detail for {self.broker_service_history} with tracking ID {self.website_tracking_id}"
