from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import re

User = settings.AUTH_USER_MODEL


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        USER = "USER", "User"
        ADMIN = "ADMIN", "Admin"
        SUPPORT = "SUPPORT", "Support"
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    total_savings = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00
    )    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    langage_preference = models.CharField(max_length=10, default="en"
                                          )

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.USER
                            )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Normalize phone number before saving to keep storage consistent       
        if self.is_superuser:
            self.role = self.Roles.ADMIN
            self.is_staff = True
            self.is_verified = True

        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.is_active = False
        self.save()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"

class BVN(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bvn"
    )
    bvn_number = models.CharField(max_length=11, unique=True)
    is_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    verified_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.bvn_number}"
    
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.is_active = False
        self.save()