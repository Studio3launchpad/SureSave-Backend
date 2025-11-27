# tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import AutoSavingSchedule, SavingsGoal, UserSavingPlan
from decimal import Decimal

@shared_task
def process_autosavings():
    """
    This task runs each minute/hour (configure in beat) and:
    - finds active schedules due now (matching frequency + time)
    - attempts to withdraw from user's wallet and credit their goal/user_plan
    - records a Transaction (you must implement)
    """
    now = timezone.localtime()
    schedules = AutoSavingSchedule.objects.filter(is_active=True)
    # naive check: time_of_day hour+minute matches (improve for production)
    for schedule in schedules:
        scheduled_time = schedule.time_of_day
        # check if schedule.time_of_day equals now's time: compare hour and minute only
        if scheduled_time.hour == now.time().hour and scheduled_time.minute == now.time().minute:
            # Determine target: goal or user_plan
            amount = schedule.amount
            # TODO: Integrate with wallet/transaction to actually move funds:
            # - debit user's wallet
            # - create Transaction record
            # - credit to SavingsGoal.saved_amount or UserSavingPlan.current_balance
            if schedule.goal:
                goal = schedule.goal
                goal.saved_amount = (goal.saved_amount or Decimal("0.00")) + Decimal(str(amount))
                if goal.saved_amount >= goal.target_amount:
                    goal.status = "completed"
                goal.save()
            elif schedule.user_plan:
                user_plan = schedule.user_plan
                user_plan.current_balance = (user_plan.current_balance or Decimal("0.00")) + Decimal(str(amount))
                user_plan.save()
    return "OK"
