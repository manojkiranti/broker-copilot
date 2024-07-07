from django.contrib import admin
from .models import Service, BrokerServiceHistory, BrokerServiceHistoryDetail

admin.register(Service)
admin.register(BrokerServiceHistory)
admin.register(BrokerServiceHistoryDetail)