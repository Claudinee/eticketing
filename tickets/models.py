
# Create your models here.
from django.db import models

class Organizer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    ticket_number = models.CharField(max_length=16, unique=True)
    personal_id = models.CharField(max_length=16, unique=True)  # NID or Passport
    is_paid = models.BooleanField(default=False)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='tickets')

    def __str__(self):
        return f"Ticket {self.ticket_number} for {self.personal_id}"

class Transaction(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for {self.ticket.ticket_number}"