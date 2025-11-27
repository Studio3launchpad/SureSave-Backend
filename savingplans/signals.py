from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import GroupContribution, GroupMember

@receiver(post_save, sender=GroupContribution)
def update_member_contribution(sender, instance, created, **kwargs):
    """
    When a contribution is created, increment the member.amount_contributed.
    """
    if created:
        member = instance.member
        member.amount_contributed = (member.amount_contributed or 0) + instance.amount
        member.save()
