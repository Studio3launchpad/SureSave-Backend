from django.db import models
from django.conf import settings
from decimal import Decimal
User = settings.AUTH_USER_MODEL

class Wallet(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.user.email} - Balance: {self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('transfer', 'Transfer'),
        ('withdrawal', 'Withdrawal'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions"
    )
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    transaction_type = models.CharField(
        max_length=30, choices=TRANSACTION_TYPES_CHOICES
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.transaction_type.title()} of {self.amount} on {self.timestamp}"
    
class TargetSavings(models.Model):
    SAVING_FREQUENCY = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    WEEK_DAY = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    SAVING_TIME = [
        ('12:00 AM', '12:00 AM'),
        ('1:00 AM', '1:00 AM'),
        ('2:00 AM', '2:00 AM'),
        ('3:00 AM', '3:00 AM'),
        ('4:00 AM', '4:00 AM'),
        ('5:00 AM', '5:00 AM'),
        ('6:00 AM', '6:00 AM'),
        ('7:00 AM', '7:00 AM'),
        ('8:00 AM', '8:00 AM'),
        ('9:00 AM', '9:00 AM'),
        ('10:00 AM', '10:00 AM'),
        ('11:00 AM', '11:00 AM'),
        ('12:00 PM', '12:00 PM'),
        ('1:00 PM', '1:00 PM'),
        ('2:00 PM', '2:00 PM'),
        ('3:00 PM', '3:00 PM'),
        ('4:00 PM', '4:00 PM'),
        ('5:00 PM', '5:00 PM'),
        ('6:00 PM', '6:00 PM'),
        ('7:00 PM', '7:00 PM'),
        ('8:00 PM', '8:00 PM'),
        ('9:00 PM', '9:00 PM'),
        ('10:00 PM', '10:00 PM'),
        ('11:00 PM', '11:00 PM'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="target_savings"
    )
    target_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    saving_frequency = models.CharField(max_length=50, choices=SAVING_FREQUENCY, default='weekly')
    week_day = models.CharField(max_length=20, choices=WEEK_DAY, default='monday')
    time = models.TimeField(choices=SAVING_TIME, default='12:00 AM')
    start_date = models.DateField()
    end_date = models.DateField()
    contribution_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00")
    )
    current_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Target Savings of {self.user.email} - Target: {self.target_amount} by {self.target_date}"

class PublicGroupTargetSavings(models.Model):
    SAVING_FREQUENCY = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    WEEK_DAY = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    SAVING_TIME = [
        ('12:00 AM', '12:00 AM'),
        ('1:00 AM', '1:00 AM'),
        ('2:00 AM', '2:00 AM'),
        ('3:00 AM', '3:00 AM'),
        ('4:00 AM', '4:00 AM'),
        ('5:00 AM', '5:00 AM'),
        ('6:00 AM', '6:00 AM'),
        ('7:00 AM', '7:00 AM'),
        ('8:00 AM', '8:00 AM'),
        ('9:00 AM', '9:00 AM'),
        ('10:00 AM', '10:00 AM'),
        ('11:00 AM', '11:00 AM'),
        ('12:00 PM', '12:00 PM'),
        ('1:00 PM', '1:00 PM'),
        ('2:00 PM', '2:00 PM'),
        ('3:00 PM', '3:00 PM'),
        ('4:00 PM', '4:00 PM'),
        ('5:00 PM', '5:00 PM'),
        ('6:00 PM', '6:00 PM'),
        ('7:00 PM', '7:00 PM'),
        ('8:00 PM', '8:00 PM'),
        ('9:00 PM', '9:00 PM'),
        ('10:00 PM', '10:00 PM'),
        ('11:00 PM', '11:00 PM'),
    ]
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="target_savings"
    )
    target_name = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    saving_frequency = models.CharField(max_length=50, choices=SAVING_FREQUENCY, default='weekly')
    week_day = models.CharField(max_length=20, choices=WEEK_DAY, default='monday')
    time = models.TimeField(choices=SAVING_TIME, default='12:00 AM')
    start_date = models.DateField()
    end_date = models.DateField()
    contribution_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00")
    )
    image = models.ImageField(upload_to='public_target_savings/', blank=True, null=True)
    current_amount = models.DecimalField(
        max_digits=18, decimal_places=2, default=Decimal("0.00")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Target Savings of {self.user.email} - Target: {self.target_amount} by {self.target_date}"
    
    