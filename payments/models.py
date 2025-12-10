from django.db import models
from django.conf import settings
import random

User = settings.AUTH_USER_MODEL

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cards')
    card_holder_name = models.CharField(max_length=255)
    card_number = models.CharField(max_length=20)
    expiry_date = models.CharField(null=True, max_length=5)  # MM/YY format
    cvv = models.CharField(max_length=4)

    is_default = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def generate_verification_code(self):
        code = random.randint(100000, 999999)
        self.verification_code = str(code)
        self.save()
        return code
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.card_holder_name} - {self.card_number[-4:]}"