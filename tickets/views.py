#from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Ticket, Organizer, Transaction
from .serializers import TicketSerializer, OrganizerSerializer, TransactionSerializer
import random
import string
from django.core.mail import send_mail

class OrganizerViewSet(viewsets.ModelViewSet):
    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def create(self, request, *args, **kwargs):
        # Generate a random ticket number
        ticket_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        request.data['ticket_number'] = ticket_number
        return super().create(request, *args, **kwargs)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        # Get the ticket and organizer
        ticket = Ticket.objects.get(ticket_number=request.data['ticket'])
        organizer = ticket.organizer

        # Update the organizer's total amount
        organizer.total_amount += float(request.data['amount'])
        organizer.save()

        # Mark the ticket as paid
        ticket.is_paid = True
        ticket.save()

        # Notify the organizer via email
        send_mail(
            'New Ticket Purchase',
            f'A ticket has been purchased for {ticket.personal_id}. Amount: {request.data["amount"]}',
            'noreply@eticketing.com',
            [organizer.email],
            fail_silently=False,
        )

        return super().create(request, *args, **kwargs)