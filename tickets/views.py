from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Ticket, Organizer, Transaction, Dependent
from .serializers import TransactionSerializer, OrganizerSerializer, TicketSerializer, DependentSerializer
import random
import string
from decimal import Decimal
from django.shortcuts import render
import qrcode
from io import BytesIO
from django.core.mail import EmailMessage
from .models import Dependent

# ----------------------------------------
# Frontend view
# ----------------------------------------
def home_view(request):
    """Render the frontend template"""
    return render(request, 'index.html')


# ----------------------------------------
# Organizer API
# ----------------------------------------
class OrganizerViewSet(viewsets.ModelViewSet):
    queryset = Organizer.objects.all()
    serializer_class = OrganizerSerializer


# ----------------------------------------
# Ticket API
# ----------------------------------------
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class DependentViewSet(viewsets.ModelViewSet):
    queryset = Dependent.objects.all()
    serializer_class = DependentSerializer


# ----------------------------------------
# Transaction API with unified purchase
# ----------------------------------------
class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def create(self, request):
        # Generate random ticket number
        ticket_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        # Fetch organizer
        organizer_id = request.data.get('organizer')
        if not organizer_id:
            return Response({"error": "Organizer ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            organizer = Organizer.objects.get(id=organizer_id)
        except Organizer.DoesNotExist:
            return Response({"error": "Organizer does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch category and price
        category = request.data.get('category')
        category_prices = {
            'VVIP': Decimal('15000'),
            'VIP': Decimal('10000'),
            'REGULAR': Decimal('5000'),
            'ADULT': Decimal('5000'),
            'CHILD': Decimal('2500')
        }
        if not category or category not in category_prices:
            return Response({"error": "Valid ticket category is required."}, status=status.HTTP_400_BAD_REQUEST)

        amount = category_prices[category]

        # Determine if ticket is for child
        dependent_id = request.data.get('dependent_id')
        personal_id = request.data.get('personal_id')

        if category == 'CHILD' or dependent_id:
            # Child ticket
            if not dependent_id:
                return Response({"error": "Dependent ID is required for child ticket."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                dependent = Dependent.objects.get(id=dependent_id)
            except Dependent.DoesNotExist:
                return Response({"error": "Dependent does not exist."}, status=status.HTTP_404_NOT_FOUND)

            if Ticket.objects.filter(dependent=dependent).exists():
                return Response({"error": "This dependent already has a ticket."}, status=status.HTTP_400_BAD_REQUEST)

            ticket = Ticket.objects.create(
                ticket_number=ticket_number,
                dependent=dependent,
                organizer=organizer,
                category=category
            )
            ticket_info = f"Child: {dependent.full_name} (Guardian ID: {dependent.guardian_id})"

        else:
            # Adult ticket
            if not personal_id:
                return Response({"error": "Personal ID is required for adult ticket."}, status=status.HTTP_400_BAD_REQUEST)
            if Ticket.objects.filter(personal_id=personal_id).exists():
                return Response({"error": "This personal ID has already been used."}, status=status.HTTP_400_BAD_REQUEST)

            ticket = Ticket.objects.create(
                ticket_number=ticket_number,
                personal_id=personal_id,
                organizer=organizer,
                category=category
            )
            ticket_info = f"Adult ID: {personal_id}"

        # Create transaction
        transaction = Transaction.objects.create(ticket=ticket, amount=amount)

        # Update organizer total
        organizer.total_amount += amount
        organizer.save()

        # Mark ticket as paid
        ticket.is_paid = True
        ticket.save()

        # Generate QR code
        qr_data = f"Ticket Number: {ticket.ticket_number}\n{ticket_info}\nCategory: {category}\nPrice: {amount} RWF"
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)

        # Optional: send email
        try:
            email = EmailMessage(
                subject='New Ticket Purchase',
                body=f'A ticket has been purchased for {ticket_info}. Category: {category}, Amount: {amount} RWF',
                from_email='noreply@eticketing.com',
                to=[organizer.email],
            )
            email.attach(f"{ticket.ticket_number}.png", buffer.read(), 'image/png')
            email.send(fail_silently=True)
        except Exception as e:
            print("Email sending failed:", e)

        # Return serialized transaction
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
