from django.contrib import admin
from .models import Opportunity, ContactsOpportunity, Stage

admin.site.register(Opportunity)
admin.site.register(ContactsOpportunity)
admin.site.register(Stage)