#!/bin/bash
apt-get update
apt-get install -y wkhtmltopdf

# Start the Django application
gunicorn --bind=0.0.0.0 --timeout 600 copilot.wsgi
