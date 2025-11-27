from django.db import models
from django.conf import settings
from django.conf import settings
from decimal import Decimal

User = settings.AUTH_USER_MODEL

class SavingPlan(models.Model):
    PLAN_TYPES = [
        ("flex", "Flexible"),
        ("target", "Target"),
        ("vault", "Locked"),
        ("group", "Group"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)   # e.g. 10.50%

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserSavingPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SavingPlan, on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
    

class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    target_date = models.DateField()
    is_public = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
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
    week_day = models.CharField(max_length=20, choices=WEEK_DAY, default='monday')
    image = models.ImageField(upload_to='savings_goals/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title    

    
class BankAccountModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bank_accounts"
    )
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20)
    account_name = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.bank_name} ({self.account_number})"
    
class GroupSavingPlan(models.Model):
    CYCLES = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
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

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")

    name = models.CharField(max_length=255)
    description = models.TextField()

    contribution_cycle = models.CharField(max_length=10, choices=CYCLES)
    week_day = models.CharField(max_length=10, choices=WEEK_DAY, default='monday')
    contribution_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"), null=True, blank=True)
    image = models.ImageField(upload_to='group_saving_plans/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AutoSavingSchedule(models.Model):
    FREQUENCY = [
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal = models.ForeignKey(SavingsGoal, on_delete=models.CASCADE, null=True, blank=True)
    user_plan = models.ForeignKey(UserSavingPlan, on_delete=models.CASCADE, null=True, blank=True)

    # Only one of the two should be filled

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    frequency = models.CharField(max_length=20, choices=FREQUENCY)

    weekday = models.CharField(
        max_length=10,
        choices=[
            ("monday", "Monday"),
            ("tuesday", "Tuesday"),
            ("wednesday", "Wednesday"),
            ("thursday", "Thursday"),
            ("friday", "Friday"),
            ("saturday", "Saturday"),
            ("sunday", "Sunday"),
        ],
        null=True,
        blank=True,
    )

    time_of_day = models.TimeField(default="00:00")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} schedule - {self.frequency}"



class GroupMember(models.Model):
    ROLE = [
        ("admin", "Admin"),
        ("member", "Member"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(GroupSavingPlan, on_delete=models.CASCADE, related_name="members")

    role = models.CharField(max_length=20, choices=ROLE, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "group")

    def __str__(self):
        return f"{self.user.email} - {self.group.name}"

    def __str__(self):
        return f"{self.user} in {self.group}"
    
    def contribute(self, amount):
        self.amount_contributed += amount
        self.save()
    def leave_group(self):
        self.delete()

    def promote_to_admin(self):
        self.role = "admin"
        self.save()
    
    def createGroup(cls, name, description, target_amount, creator):
        group = cls.objects.create(
            name=name,
            description=description,
            target_amount=target_amount
        )
        GroupMember.objects.create(
            user=creator,
            group=group,
            role="admin"
        )
        return group
    
class GroupContribution(models.Model):
    member = models.ForeignKey(GroupMember, on_delete=models.CASCADE)
    group = models.ForeignKey(GroupSavingPlan, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date_contributed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.user.email} contributed {self.amount}"


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default="NGN")

    def __str__(self):
        return f"{self.user.email} Wallet"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # For transfers
    receiver_wallet = models.ForeignKey(
        Wallet, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_transfers"
    )

    def __str__(self):
        return f"{self.type} - {self.amount} - {self.reference}"