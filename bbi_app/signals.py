# In signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import DriverProfile

@receiver(post_save, sender=User)
def create_driver_profile(sender, instance, created, **kwargs):
    if created:
        DriverProfile.objects.create(user=instance)