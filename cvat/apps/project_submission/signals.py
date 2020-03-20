from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProjectSubmission

@receiver(post_save, sender=ProjectSubmission)
def update_submission_map(sender, instance, created, **kwargs):
    if created:
        instance.update_mean_average_precision()
