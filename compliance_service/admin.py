from django.contrib import admin
from .models import SystemPrompt, Note, ComplianceSystemPrompt

admin.site.register(SystemPrompt)
admin.site.register(Note)
admin.site.register(ComplianceSystemPrompt)
