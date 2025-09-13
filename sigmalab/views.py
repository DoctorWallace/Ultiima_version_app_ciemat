# sigmalab/views.py
from django.shortcuts import render, redirect
from functools import wraps
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.utils import OperationalError, ProgrammingError
from django.db.models import Count
from django.contrib.auth import get_user_model

from .models import Sample, Solicitud
from .forms import SampleForm, DiarioEntradaForm

from django.contrib.auth.decorators import login_required as _login_required, user_passes_test as _user_passes_test

def login_required_dtf(view):
    """Requiere autenticación y que la sesión sea del módulo DTF.

    Evita que un usuario autenticado en ICTS aparezca como "logueado" en DTF
    sin haber pasado por el login DTF. Si no está en módulo DTF, se redirige
    al login específico conservando el "next".
    """
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login_dtf')}?next=" + request.get_full_path())
        if request.session.get("module") != "dtf":
            return redirect(f"{reverse('accounts:login_dtf')}?next=" + request.get_full_path())
        return view(request, *args, **kwargs)
    return _wrapped

def user_passes_test_dtf(test_func):
    return _user_passes_test(test_func, login_url="/cuentas/login/dtf/")



# --- helpers de rol ---
def is_technician_sl(user):
    """Técnico S‑LAB (robusto a acentos/variantes)."""
    return (
        user.is_authenticated and (
            user.is_superuser or user.groups.filter(name__icontains="S-LAB").exists()
        )
    )
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
@user_passes_test_dtf(is_technician_sl)
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

@login_required_dtf
def diario_solicitud(request, pk):
    sol = get_model_or_404(Solicitud, pk=pk) if False else None
    try:
        sol = Solicitud.objects.get(pk=pk)
    except Solicitud.DoesNotExist:
        return redirect("sigmalab:mis-solicitudes")
    # Permisos: autor con autonomía o técnico
    if not (sol.solicitante_id == request.user.id and sol.autonomo) and not is_technician(request.user):
        messages.error(request, "No tienes permiso para registrar entradas de diario en esta solicitud.")
        return redirect("sigmalab:detalle-solicitud", pk=pk)

    if request.method == "POST":
        form = DiarioEntradaForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.solicitud = sol
            entry.autor = request.user
            entry.save()
            messages.success(request, "Entrada registrada en el diario.")
            return redirect("sigmalab:diario-solicitud", pk=pk)
    else:
        form = DiarioEntradaForm()

    entradas = sol.diario.select_related("autor").all()
    return render(request, "sigmalab/diario.html", {"solicitud": sol, "form": form, "entradas": entradas})

@login_required_dtf
@user_passes_test_dtf(is_technician)
def toggle_autonomia(request, pk):
    sol = Solicitud.objects.filter(pk=pk).first()
    if not sol:
        return redirect("sigmalab:todas-solicitudes")
    sol.autonomo = not sol.autonomo
    sol.save(update_fields=["autonomo"])
    messages.success(request, f"Autonomía {'activada' if sol.autonomo else 'desactivada'} para la solicitud {sol.pk}.")
    return redirect("sigmalab:detalle-solicitud", pk=pk)

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
@user_passes_test(is_technician_sl)
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

