import json
from django.conf import settings

def load_json_data():
    file_path = settings.BASE_DIR / 'compliance_service' / 'data' / 'data.json'
    with open(file_path, 'r') as file:
        return json.load(file)