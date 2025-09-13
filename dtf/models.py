from django.db import models
from django.conf import settings


class DTFUserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dtf_profile")
    is_ciemat = models.BooleanField(default=False)
    departamento = models.CharField(max_length=50, blank=True)
    matricula = models.CharField(max_length=50, blank=True)
    telefono_interno = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"DTFProfile({self.user_id})"
