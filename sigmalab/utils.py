def is_tecnico(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name="Técnicos Σ-LAB").exists())
