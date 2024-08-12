#!/bin/sh

# Start the SSH service
service ssh start

# Collect static files
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn --bind 0.0.0.0:8000 copilot.wsgi:application