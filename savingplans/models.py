from django.db import models
from django.conf import settings

class SavingPlan(models.Model):
    class PlanType(models.TextChoices):
        BASIC = "CASUAL", "casual"
        PREMIUM = "GOAL_GETTER", "goal_getter"
        GOLD = "SHOWCASE", "showcase"
    name = models.CharField(max_length=255)
    description = models.TextField()
    plan_type = models.CharField(
        max_length=100,
        choices=PlanType.choices,
        default=PlanType.BASIC,
    )
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration_day = models.IntegerField(blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserSavingPlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saving_plans"
    )
    plan = models.ForeignKey(
        SavingPlan, on_delete=models.CASCADE, related_name="user_saving_plans"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.saving_plan.name}"
    

class SavingsGoal(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active',
        COMPLETED = 'COMPLETED', 'Completed',
        CANCELED = 'CANCELED', 'Canceled',

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')
    name = models.CharField(max_length=255)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    target_date = models.DateField()
    status = models.CharField(
        max_length=100,
        choices=StatusChoices,
        default=StatusChoices.ACTIVE
    )
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.email} - {self.name}"
    
class BvnModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bvn"
    )
    bvn_number = models.CharField(max_length=11, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.bvn_number}"
    
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
    name = models.CharField(max_length=255)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    contribution_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cycle = models.CharField(max_length=20, choices=[
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ], default="monthly")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_groups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(GroupSavingPlan, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    amount_contributed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    role = models.CharField(max_length=20, choices=[
        ("member", "Member"),
        ("admin", "Admin"),
    ], default="member")

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
    group = models.ForeignKey(GroupSavingPlan, on_delete=models.CASCADE, related_name="contributions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    contributed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} contributed {self.amount} to {self.group}"