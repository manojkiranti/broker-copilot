from django.contrib import admin

# Register your models here.
from .models import Bank, Policy, BankPolicy, ChatSession, Message

admin.site.register(Bank)
admin.site.register(Policy)
admin.site.register(BankPolicy)
admin.site.register(ChatSession)
admin.site.register(Message)
