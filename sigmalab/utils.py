def is_tecnico(user):
    """Devuelve True si el usuario es técnico DTF.

    Considera superuser/staff o pertenencia a cualquier grupo
    "tecnico_responsable_*" (S-LAB, S-MEC, S-DP, ...).
    """
    if not getattr(user, "is_authenticated", False):
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True
    return user.groups.filter(name__startswith="tecnico_responsable_").exists()

