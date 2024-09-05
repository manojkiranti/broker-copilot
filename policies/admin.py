from django.contrib import admin

# Register your models here.
from .models import Bank, Policy, BankPolicy

admin.site.register(Bank)
admin.site.register(Policy)
admin.site.register(BankPolicy)
