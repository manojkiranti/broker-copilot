from django.contrib import admin
from .models import Service, BrokerServiceHistory

admin.register(Service)
admin.register(BrokerServiceHistory)