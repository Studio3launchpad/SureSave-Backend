from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

class JobSavings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_savings")
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    savings_goal = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"
