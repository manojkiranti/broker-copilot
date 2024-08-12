#!/bin/sh

# Start the SSH service
service ssh start

# Log the status of the SSH service for debugging
service ssh status

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:8000 copilot.wsgi:application