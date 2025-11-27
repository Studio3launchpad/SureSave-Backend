from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
import re
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email or phone_number is the unique identifiers
    for authentication instead of usernames.
    """
    class UserQuerySet(models.QuerySet):
        def active(self):
            return self.filter(is_deleted=False)

    def get_queryset(self):
        return self.UserQuerySet(self.model, using=self._db).active()

    def normalize_phone(self, phone_number: str) -> str:
        """Return a digits-only phone number string (or empty string if None)."""
        if not phone_number:
            return ""
        return re.sub(r"\D", "", phone_number)

    def create_user(self, email, phone_number, frist_name, last_name, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        phone_number = self.normalize_phone(phone_number)
        if not phone_number:
            raise ValueError(_("The phone number must be set"))
        role = extra_fields.get('role', 'USER')
        extra_fields['role'] = role
        user = self.model(
            email=email, phone_number=phone_number, frist_name=frist_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        if role in ['ADMIN', 'SUPPORT']:
            user.is_staff = True
        else:
            user.is_staff = False
        user.save()
        return user

    def create_superuser(self, email, phone_number, frist_name, last_name, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        phone_number = self.normalize_phone(phone_number)
        return self.create_user(email, phone_number, frist_name, last_name, password, **extra_fields)
