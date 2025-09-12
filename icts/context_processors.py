# App_ciemat/icts/context_processors.py
def icts_ui(request):
    user = request.user
    role = ""
    if user.is_authenticated:
        if user.is_superuser:
            role = "Admin"
        elif user.groups.filter(name__iexact="managers").exists():
            role = "Manager"
        elif user.groups.filter(name__iexact="responsables").exists():
            role = "Responsable"
        elif user.groups.filter(name__iexact="revisores").exists():
            role = "Revisor"
        else:
            role = "Usuario"
    return {"icts_role_name": role}
