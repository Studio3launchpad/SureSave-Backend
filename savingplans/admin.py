from django.contrib import admin
from savingplans.models import (
    SavingPlan, 
    UserSavingPlan, 
    SavingsGoal, 
    AutoSavingSchedule, 
    GroupSavingPlan, 
    GroupMember, 
    GroupContribution, 
    Wallet, 
    Transaction,
)


@admin.register(SavingPlan)
class SavingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "plan_type", "interest_rate", "min_amount", "max_amount", "created_at")
    search_fields = ("name",)
    list_filter = ("plan_type", "created_at")


@admin.register(UserSavingPlan)
class UserSavingPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "current_balance", "start_date", "end_date", "is_active")
    search_fields = ("user__email", "plan__name")
    list_filter = ("is_active",)


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "target_amount", "saved_amount", "target_date", "status", "is_public")
    search_fields = ("user__email", "title")
    list_filter = ("status", "is_public")


@admin.register(AutoSavingSchedule)
class AutoSavingScheduleAdmin(admin.ModelAdmin):
    list_display = ("user", "goal", "user_plan", "amount", "frequency", "weekday", "time_of_day", "is_active", "created_at")
    search_fields = ("user__email",)
    list_filter = ("frequency", "weekday", "is_active")


@admin.register(GroupSavingPlan)
class GroupSavingPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "contribution_amount", "target_amount", "contribution_cycle", "week_day", "created_at")
    search_fields = ("name", "created_by__email")
    list_filter = ("contribution_cycle", "week_day", "created_at")


@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "group", "role", "joined_at")
    search_fields = ("user__email", "group__name")
    list_filter = ("role", "joined_at")


@admin.register(GroupContribution)
class GroupContributionAdmin(admin.ModelAdmin):
    list_display = ("member", "group", "amount", "date_contributed")
    search_fields = ("member__user__email", "group__name")
    list_filter = ("date_contributed",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "currency")
    search_fields = ("user__email",)
    # created_at does not exist in Wallet → removed


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "amount", "type", "reference", "created_at", "receiver_wallet")
    search_fields = ("wallet__user__email", "reference")
    list_filter = ("type", "created_at")
