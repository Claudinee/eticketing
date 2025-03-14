from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Ticket, Organizer, Transaction
from .serializers import TransactionSerializer, OrganizerSerializer, TicketSerializer
import random
import string
from django.core.mail import send_mail
from decimal import Decimal  # Import Decimal


class OrganizerViewSet(viewsets.ModelViewSet):
    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request, *args, **kwargs):
        # Generate a random ticket number
        ticket_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # Fetch the organizer (assuming organizer_id is provided in the request)
        organizer_id = request.data.get('organizer')
        if not organizer_id:
            return Response({"error": "Organizer ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            organizer = Organizer.objects.get(id=organizer_id)
        except Organizer.DoesNotExist:
            return Response({"error": "Organizer does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Create a new ticket
        personal_id = request.data.get('personal_id')  # Assuming personal_id is provided in the request
        if not personal_id:
            return Response({"error": "Personal ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        ticket = Ticket.objects.create(
            ticket_number=ticket_number,
            personal_id=personal_id,
            organizer=organizer
        )

        # Create the transaction
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction.objects.create(
            ticket=ticket,
            amount=amount
        )

        # Update the organizer's total amount
        organizer.total_amount += float(amount)
        organizer.save()

        # Mark the ticket as paid
        ticket.is_paid = True
        ticket.save()

        # Notify the organizer via email
        send_mail(
            'New Ticket Purchase',
            f'A ticket has been purchased for {ticket.personal_id}. Amount: {amount}',
            'noreply@eticketing.com',
            [organizer.email],
            fail_silently=False,
        )

        # Return the transaction details
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)