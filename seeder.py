# seeds.py (or any other name you prefer)

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'copilot.settings')

import django
django.setup()

from services.models import Service

def seed_services():
    services = [
        {'name': 'Broker Service History', 'url': 'broker_service_history', 'description': 'This is service 1', 'status': 'active'},
    ]

    for service in services:
        Service.objects.create(**service)

if __name__ == '__main__':
    seed_services()