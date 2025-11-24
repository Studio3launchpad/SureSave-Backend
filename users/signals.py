from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile
from allauth.account.signals import email_confirmed
from django.dispatch import receiver as signal_receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    profile, created = UserProfile.objects.get_or_create(user=instance)
    if not created:
        profile.save()


# When allauth confirms an email address, mark the corresponding user as verified
@signal_receiver(email_confirmed)
def allauth_email_confirmed(request, email_address, **kwargs):
    user = getattr(email_address, "user", None)
    if user:
        # set is_verified flag and save
        user.is_verified = True
        user.save()
