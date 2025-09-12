from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

def create_sigmalab_groups(sender, **kwargs):
    # Crea (si faltan) los grupos
    tecnicos, _ = Group.objects.get_or_create(name="Técnicos Σ-LAB")
    usuarios, _ = Group.objects.get_or_create(name="Usuarios Σ-LAB")
    # (Opcional) asigna permisos finos cuando tengas los modelos listos
    # por ahora lo dejamos vacío; los checks los haremos por pertenencia al grupo
