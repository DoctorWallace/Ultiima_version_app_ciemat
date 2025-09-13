from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group


@receiver(post_migrate)
def ensure_mec_groups(sender, **kwargs):
    if sender.name != 'mec':
        return
    Group.objects.get_or_create(name="Tecnicos responsables S-MEC")
    Group.objects.get_or_create(name="Tecnicos S-MEC")
