from django.db import models
import hashlib

class Organizer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name


class Dependent(models.Model):
    guardian_id = models.CharField(max_length=16)  # Guardian’s NID or Passport
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    birth_certificate_no = models.CharField(max_length=50, blank=True, null=True)
    school_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} (Guardian: {self.guardian_id})"

    @property
    def fingerprint(self):
        """Generate a unique fingerprint for the child (name + DOB + guardian ID)."""
        raw = f"{self.full_name.strip().lower()}|{self.date_of_birth.isoformat()}|{self.guardian_id}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def is_under_16_on(self, date):
        """Check if the child is under 16 on a given date (event date)."""
        age = (date - self.date_of_birth).days // 365
        return age < 16


class Ticket(models.Model):
    CATEGORY_CHOICES = [
        ('VVIP', 'VVIP'),
        ('VIP', 'VIP'),
        ('REGULAR', 'Regular'),
        ('ADULT', 'Adult'),
        ('CHILD', 'Child'),
    ]

    ticket_number = models.CharField(max_length=16, unique=True)
    personal_id = models.CharField(max_length=16, blank=True, null=True)  # Adult ID
    dependent = models.ForeignKey(
        Dependent, on_delete=models.CASCADE, blank=True, null=True, related_name="tickets"
    )  # Child ticket
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='REGULAR'  # Default to REGULAR for existing rows during migration
    )
    is_paid = models.BooleanField(default=False)
    organizer = models.ForeignKey(Organizer, on_delete=models.CASCADE, related_name='tickets')

    def __str__(self):
        if self.personal_id:
            return f"Ticket {self.ticket_number} ({self.category}) for {self.personal_id}"
        elif self.dependent:
            return f"Ticket {self.ticket_number} ({self.category}) for Dependent {self.dependent.full_name}"
        return f"Ticket {self.ticket_number} ({self.category})"


class Transaction(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name='transaction')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction for {self.ticket.ticket_number} ({self.ticket.category})"
