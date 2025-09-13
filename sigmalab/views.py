"""Vistas DTF/S-LAB (SIGMALAB).

Unifica autenticación DTF y rol de técnico según nuevos grupos canónicos:
- usuarios_dtf
- tecnico_responsable_s_lab, tecnico_responsable_s_mec, tecnico_responsable_s_dp
- usuarios_autonomo_s_lab
"""

from django.shortcuts import render, redirect, get_object_or_404
from functools import wraps
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth import get_user_model
from urllib.parse import quote as urlquote

from .models import Sample, Solicitud
from .forms import SampleForm, DiarioEntradaForm
from django.contrib.auth.decorators import (
    login_required as _login_required,
    user_passes_test as _user_passes_test,
)


def login_required_dtf(view):
    """Requiere autenticación y que la sesión sea del módulo DTF."""
    @wraps(view)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login_dtf')}?next=" + urlquote(request.get_full_path()))
        if request.session.get("module") != "dtf":
            return redirect(f"{reverse('accounts:login_dtf')}?next=" + urlquote(request.get_full_path()))
        return view(request, *args, **kwargs)
    return _wrapped


def user_passes_test_dtf(test_func):
    return _user_passes_test(test_func, login_url="/accounts/login/dtf/")


# --- helpers de rol ---
def is_technician_sl(user):
    """Técnico responsable S-LAB (grupo canónico)."""
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name="tecnico_responsable_s_lab").exists()
    )


def is_technician(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__startswith="tecnico_responsable_").exists()
    )


@login_required_dtf
def dashboard(request):
    if is_technician(request.user):
        return redirect("sigmalab:panel-tecnico")
    return redirect("sigmalab:panel-usuario")


@login_required_dtf
@user_passes_test_dtf(is_technician_sl)
def panel_tecnico(request):
    pendientes = (
        Solicitud.objects.filter(estado=Solicitud.Estado.PENDIENTE)
        .select_related("solicitante")[:10]
    )
    aceptadas = (
        Solicitud.objects.filter(estado=Solicitud.Estado.ACEPTADA)
        .select_related("solicitante")[:10]
    )
    rechazadas = (
        Solicitud.objects.filter(estado=Solicitud.Estado.RECHAZADA)
        .select_related("solicitante")[:10]
    )
    recientes = (
        Solicitud.objects.select_related("solicitante").order_by("-creado_en")[:10]
    )

    contadores = {
        "pendientes": Solicitud.objects.filter(estado=Solicitud.Estado.PENDIENTE).count(),
        "en_curso": Solicitud.objects.filter(estado=Solicitud.Estado.EN_CURSO).count(),
        "aceptadas": Solicitud.objects.filter(estado=Solicitud.Estado.ACEPTADA).count(),
        "rechazadas": Solicitud.objects.filter(estado=Solicitud.Estado.RECHAZADA).count(),
    }
    return render(
        request,
        "sigmalab/panel_tecnico.html",
        {
            "pendientes": pendientes,
            "aceptadas": aceptadas,
            "rechazadas": rechazadas,
            "recientes": recientes,
            "contadores": contadores,
        },
    )


@login_required_dtf
def panel_usuario(request):
    mias = (
        Solicitud.objects.filter(solicitante=request.user)
        .select_related("solicitante")
        .order_by("-creado_en")[:10]
    )

    estados = (
        Solicitud.objects.filter(solicitante=request.user).values("estado").annotate(n=Count("id"))
    )
    recuento = {"pendiente": 0, "aceptada": 0, "rechazada": 0, "en_curso": 0, "finalizada": 0}
    for e in estados:
        recuento[e["estado"]] = e["n"]

    return render(
        request,
        "sigmalab/panel_usuario.html",
        {
            "mias": mias,
            "recuento": recuento,
        },
    )


@login_required_dtf
def diario_solicitud(request, pk):
    sol = get_object_or_404(Solicitud, pk=pk)
    if not (sol.solicitante_id == request.user.id and sol.autonomo) and not is_technician(
        request.user
    ):
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
    messages.success(
        request, f"Autonomía {'activada' if sol.autonomo else 'desactivada'} para la solicitud {sol.pk}."
    )
    return redirect("sigmalab:detalle-solicitud", pk=pk)


@login_required_dtf
def sample_list(request):
    samples = Sample.objects.all()
    return render(request, "sigmalab/sample_list.html", {"samples": samples})


@login_required_dtf
def sample_create(request):
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.owner = request.user
            sample.save()
            messages.success(request, "Muestra creada correctamente.")
            return redirect("sigmalab:sample-list")
    else:
        form = SampleForm()
    return render(request, "sigmalab/sample_form.html", {"form": form})


@login_required_dtf
@user_passes_test_dtf(is_technician_sl)
def usuarios_overview(request):
    User = get_user_model()
    usuarios = User.objects.annotate(num_solicitudes=Count("solicitudes")).order_by("-date_joined")
    recientes = usuarios[:10]
    return render(
        request,
        "sigmalab/usuarios_overview.html",
        {
            "usuarios": usuarios,
            "recientes": recientes,
        },
    )

