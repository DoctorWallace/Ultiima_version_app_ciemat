# sigmalab/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Count
from django.contrib.auth import get_user_model

from .models import Sample, Solicitud
from .forms import SampleForm

from django.contrib.auth.decorators import login_required as _login_required, user_passes_test as _user_passes_test

def login_required_dtf(view):
    return _login_required(login_url="/cuentas/login/dtf/")(view)

def user_passes_test_dtf(test_func):
    return _user_passes_test(test_func, login_url="/cuentas/login/dtf/")



# --- helpers de rol ---
def is_technician(user):
    return (
        user.is_authenticated and (
            user.is_superuser or user.groups.filter(name="Técnicos Σ-LAB").exists()
        )
    )

# ---------- REDIRECTOR AL PANEL SEGÚN ROL ----------
@login_required_dtf
def dashboard(request):
    if is_technician(request.user):
        return redirect("sigmalab:panel-tecnico")
    return redirect("sigmalab:panel-usuario")

# ---------- PANEL TÉCNICO ----------
@login_required_dtf
@user_passes_test_dtf(is_technician)
def panel_tecnico(request):
    # Listas cortas para la portada (puedes ampliar el límite)
    pendientes  = Solicitud.objects.filter(estado="pendiente").select_related("solicitante")[:10]
    aceptadas   = Solicitud.objects.filter(estado="aceptada").select_related("solicitante")[:10]
    rechazadas  = Solicitud.objects.filter(estado="rechazada").select_related("solicitante")[:10]

    # Recuento rápido
    contadores = {
        "pendientes": Solicitud.objects.filter(estado="pendiente").count(),
        "aceptadas":  Solicitud.objects.filter(estado="aceptada").count(),
        "rechazadas": Solicitud.objects.filter(estado="rechazada").count(),
    }
    return render(request, "sigmalab/panel_tecnico.html", {
        "pendientes": pendientes,
        "aceptadas": aceptadas,
        "rechazadas": rechazadas,
        "contadores": contadores,
    })

# ---------- PANEL USUARIO ----------
@login_required_dtf
def panel_usuario(request):
    # Mis últimas solicitudes
    mias = Solicitud.objects.filter(solicitante=request.user).select_related("solicitante").order_by("-creado_en")[:10]

    # Recuento por estado
    estados = (
        Solicitud.objects.filter(solicitante=request.user)
        .values("estado").annotate(n=Count("id"))
    )
    # Pasar a dict {estado: n}
    recuento = {"pendiente":0,"aceptada":0,"rechazada":0,"en_curso":0,"finalizada":0}
    for e in estados:
        recuento[e["estado"]] = e["n"]

    return render(request, "sigmalab/panel_usuario.html", {
        "mias": mias,
        "recuento": recuento,
    })

# ---------- VISTAS MUESTRAS (tuyas) ----------
@login_required_dtf
def sample_list(request):
    samples = Sample.objects.all()  # .filter(owner=request.user) si quieres
    return render(request, "sigmalab/sample_list.html", {"samples": samples})

@login_required_dtf
def sample_create(request):
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.applicant = request.user
            sample.save()
            messages.success(request, "Muestra creada correctamente.")
            return redirect("sigmalab:sample-list")
    else:
        form = SampleForm()
    return render(request, "sigmalab/sample_form.html", {"form": form})

# ---------- VISTA USUARIOS (para técnicos) ----------
@login_required_dtf
@user_passes_test(is_technician)
def usuarios_overview(request):
    User = get_user_model()
    # Alta recientes y nº de solicitudes por usuario
    usuarios = (
        User.objects
        .annotate(num_solicitudes=Count("solicitudes"))
        .order_by("-date_joined")
    )
    recientes = usuarios[:10]
    return render(request, "sigmalab/usuarios_overview.html", {
        "usuarios": usuarios,
        "recientes": recientes,
    })
