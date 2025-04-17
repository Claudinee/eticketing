from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Ticket, Organizer, Transaction
from .serializers import TransactionSerializer, OrganizerSerializer, TicketSerializer
import random
import string
from django.core.mail import send_mail
from decimal import Decimal


class OrganizerViewSet(viewsets.ModelViewSet):
    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request):
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

        # Get and validate personal_id
        personal_id = request.data.get('personal_id')
        if not personal_id:
            return Response({"error": "Personal ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if personal_id has already been used
        if Ticket.objects.filter(personal_id=personal_id).exists():
            return Response(
                {"error": "This personal ID has already been used to buy a ticket."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the ticket
        ticket = Ticket.objects.create(
            ticket_number=ticket_number,
            personal_id=personal_id,
            organizer=organizer
        )

        # Get and validate amount
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(amount)
        except Exception:
            return Response({"error": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the transaction
        transaction = Transaction.objects.create(
            ticket=ticket,
            amount=amount
        )

        # Update organizer's total amount
        if organizer.total_amount is None:
            organizer.total_amount = Decimal(0)
        organizer.total_amount += amount
        organizer.save()

        # Mark the ticket as paid
        ticket.is_paid = True
        ticket.save()

        # Send notification email
        send_mail(
            'New Ticket Purchase',
            f'Hello, a ticket has been purchased for {ticket.personal_id}. Amount: {amount}',
            'noreply@eticketing.com',
            [organizer.email],
            fail_silently=False,
        )

        # Serialize and return the transaction
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
