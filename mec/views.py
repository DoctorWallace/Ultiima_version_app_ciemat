# mec/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test as _user_passes_test
from django.urls import reverse

from .models import MecSample, MecSolicitud
from .forms import MecSampleForm, MecSolicitudForm


def login_required_dtf(view):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login_dtf')}?next=" + request.get_full_path())
        if request.session.get("module") != "dtf":
            return redirect(f"{reverse('accounts:login_dtf')}?next=" + request.get_full_path())
        return view(request, *args, **kwargs)
    return _wrapped


def is_tecnico_responsable(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__iexact="Tecnicos responsables S-MEC").exists()
    )


@login_required_dtf
def panel_usuario(request):
    mias = MecSolicitud.objects.filter(solicitante=request.user).order_by("-creado_en")[:20]
    return render(request, "mec/panel_usuario.html", {"mias": mias})


@login_required_dtf
@_user_passes_test(is_tecnico_responsable, login_url="/accounts/login/dtf/")
def panel_tecnico_responsable(request):
    pendientes = MecSolicitud.objects.filter(estado="pendiente").order_by("-creado_en")[:20]
    aceptadas = MecSolicitud.objects.filter(estado="aceptada").order_by("-creado_en")[:20]
    rechazadas = MecSolicitud.objects.filter(estado="rechazada").order_by("-creado_en")[:20]
    return render(request, "mec/panel_tecnico.html", {
        "pendientes": pendientes,
        "aceptadas": aceptadas,
        "rechazadas": rechazadas,
    })


@login_required_dtf
def sample_create(request):
    if request.method == "POST":
        form = MecSampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.owner = request.user
            sample.save()
            messages.success(request, "Muestra creada correctamente.")
            return redirect("mec:panel_usuario")
    else:
        form = MecSampleForm()
    return render(request, "mec/sample_form.html", {"form": form})


@login_required_dtf
def solicitud_create(request):
    if request.method == "POST":
        form = MecSolicitudForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.solicitante = request.user
            obj.save()
            form.save_m2m()
            messages.success(request, "Solicitud creada.")
            return redirect("mec:panel_usuario")
    else:
        form = MecSolicitudForm()
    return render(request, "mec/solicitud_form.html", {"form": form})

