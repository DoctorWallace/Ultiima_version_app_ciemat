# sigmalab/context_processors.py
def lab_role(request):
    """
    Devuelve LAB_ROLE = "TECNICO" | "USUARIO" | None
    para pintar el badge en la barra superior.
    """
    role = None
    if request.user.is_authenticated:
        if (
            request.user.is_superuser
            or request.user.is_staff
            or request.user.groups.filter(name__startswith="tecnico_responsable_").exists()
        ):
            role = "TECNICO"
        else:
            role = "USUARIO"
    return {"LAB_ROLE": role}
