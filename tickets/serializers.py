from rest_framework import serializers
from .models import Ticket, Organizer, Transaction, Dependent

class OrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organizer
        fields = '__all__'


class DependentSerializer(serializers.ModelSerializer):
    fingerprint = serializers.ReadOnlyField()  # Expose fingerprint in API, but not editable

    class Meta:
        model = Dependent
        fields = [
            'id',
            'guardian_id',
            'full_name',
            'date_of_birth',
            'birth_certificate_no',
            'school_id',
            'fingerprint',
        ]


class TicketSerializer(serializers.ModelSerializer):
    dependent = DependentSerializer(read_only=True)  # Show child info if ticket belongs to a dependent
    dependent_id = serializers.PrimaryKeyRelatedField(
        queryset=Dependent.objects.all(),
        source="dependent",
        write_only=True,
        required=False,
        allow_null=True
    )
    category = serializers.CharField(required=True)  # Add category field

    class Meta:
        model = Ticket
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    ticket_number = serializers.CharField(source='ticket.ticket_number', read_only=True)
    category = serializers.CharField(source='ticket.category', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'timestamp', 'ticket_number', 'category']
