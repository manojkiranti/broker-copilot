from django.contrib import admin
from .models import SystemPrompt, Note, NotePdf, BrokerNoteSystemprompt
# Register your models here.
admin.site.register(SystemPrompt)
admin.site.register(Note)
admin.site.register(NotePdf)
admin.site.register(BrokerNoteSystemprompt)
