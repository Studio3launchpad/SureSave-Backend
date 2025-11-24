from django.contrib import admin

from savingplans.models import SavingPlan, UserSavingPlan, SavingsGoal

@admin.register(SavingPlan)
class SavingPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'min_amount', 'max_amount', 'duration_day', 'interest_rate', 'created_at')
    search_fields = ('name', 'plan_type')
    list_filter = ('plan_type',)
@admin.register(UserSavingPlan)
class UserSavingPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'amount', 'start_date', 'end_date', 'is_active', 'created_at')
    search_fields = ('user__email', 'plan__name')
    list_filter = ('is_active',)
@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'target_amount', 'saved_amount', 'target_date', 'status', 'is_public', 'created_at')
    search_fields = ('user__email', 'name')
    list_filter = ('status', 'is_public')   
    
