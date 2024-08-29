from django.contrib import admin
from .models import SystemPrompt, Note, NotePdf
# Register your models here.
admin.site.register(SystemPrompt)
admin.site.register(Note)
admin.site.register(NotePdf)