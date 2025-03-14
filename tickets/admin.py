from django.contrib import admin

# Register your models here.
from .models import Organizer, Ticket, Transaction

admin.site.register(Organizer)
admin.site.register(Ticket)
admin.site.register(Transaction)