from django.db import models
from django.conf import settings

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        INFO = "INFO", "Information"
        WARNING = "WARNING", "Warning"
        ALERT = "ALERT", "Alert"
        MOTIVATIONAL = "MOTIVATIONAL", "Motivational"
        GOAL_ALERT = "GOAL_ALERT", "Goal Alert"
        REMINDER = "REMINDER", "Reminder"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=255,
        choices=NotificationType.choices,
        default=NotificationType.INFO,
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.notification_type} - {'Read' if self.is_read else 'Unread'}"
