from rest_framework import serializers
from .models import Ticket, Organizer, Transaction

class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
          model = Transaction
    fields = ['id', 'amount', 'status']