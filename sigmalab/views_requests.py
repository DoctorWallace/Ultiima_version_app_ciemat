from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import Solicitud
from .forms import SolicitudForm, AvanceForm, EstadoForm
from .utils import is_tecnico
from .views import login_required_dtf, user_passes_test_dtf


# --- Usuario: crear y ver sus solicitudes

@login_required_dtf
def nueva_solicitud(request):
    if request.method == "POST":
        form = SolicitudForm(request.POST)
        if form.is_valid():
            sol = form.save(commit=False)
            sol.solicitante = request.user
            sol.save()
            messages.success(request, "Solicitud creada correctamente.")
            return redirect("sigmalab:mis-solicitudes")
    else:
        form = SolicitudForm()
    return render(request, "sigmalab/solicitudes/crear.html", {"form": form})


@login_required_dtf
def mis_solicitudes(request):
    qs = Solicitud.objects.filter(solicitante=request.user).order_by("-creado_en")
    return render(request, "sigmalab/solicitudes/mis_solicitudes.html", {"solicitudes": qs})


@login_required_dtf
def detalle_solicitud(request, pk):
    sol = get_object_or_404(Solicitud.objects.prefetch_related("avances__autor"), pk=pk)
    # Usuario solo ve las suyas; técnico ve todas
    if sol.solicitante != request.user and not is_tecnico(request.user):
        messages.error(request, "No tienes permiso para ver esta solicitud.")
        return redirect("sigmalab:mis-solicitudes")
    avances = sol.avances.all()
    return render(
        request,
        "sigmalab/solicitudes/detalle.html",
        {"solicitud": sol, "avances": avances},
    )


@login_required_dtf
def nuevo_avance(request, pk):
    sol = get_object_or_404(Solicitud, pk=pk)
    if sol.solicitante != request.user and not is_tecnico(request.user):
        messages.error(request, "No tienes permiso para añadir avances a esta solicitud.")
        return redirect("sigmalab:mis-solicitudes")

    if request.method == "POST":
        form = AvanceForm(request.POST, request.FILES)
        if form.is_valid():
            av = form.save(commit=False)
            av.solicitud = sol
            av.autor = request.user
            # Si no es técnico, fuerza avance visible al usuario
            if not is_tecnico(request.user):
                av.visible_para_usuario = True
            av.save()
            messages.success(request, "Avance añadido.")
            return redirect("sigmalab:detalle-solicitud", pk=sol.pk)
    else:
        form = AvanceForm()
    return render(request, "sigmalab/solicitudes/nuevo_avance.html", {"solicitud": sol, "form": form})


# --- Técnico: bandeja, todas, cambiar estado

@login_required_dtf
@user_passes_test_dtf(is_tecnico)
def bandeja_tecnico(request):
    estado = (request.GET.get("estado") or "").strip()
    base = Solicitud.objects.select_related("solicitante")
    if estado in dict(Solicitud.Estado.choices):
        qs = base.filter(estado=estado).order_by("-creado_en")
    else:
        qs = base.filter(
            estado__in=[
                Solicitud.Estado.PENDIENTE,
                Solicitud.Estado.ACEPTADA,
                Solicitud.Estado.EN_CURSO,
            ]
        ).order_by("estado", "-creado_en")
        estado = ""
    ctx = {"solicitudes": qs, "selected_estado": estado}
    return render(request, "sigmalab/solicitudes/bandeja_tecnico.html", ctx)


@login_required_dtf
@user_passes_test_dtf(is_tecnico)
def todas_solicitudes(request):
    estado = (request.GET.get("estado") or "").strip()
    base = Solicitud.objects.select_related("solicitante")
    if estado in dict(Solicitud.Estado.choices):
        qs = base.filter(estado=estado).order_by("-creado_en")
    else:
        qs = base.order_by("-creado_en")
        estado = ""
    return render(request, "sigmalab/solicitudes/todas.html", {"solicitudes": qs, "selected_estado": estado})


@login_required_dtf
@user_passes_test_dtf(is_tecnico)
def cambiar_estado(request, pk):
    sol = get_object_or_404(Solicitud, pk=pk)
    if request.method == "POST":
        form = EstadoForm(request.POST)
        if form.is_valid():
            accion = form.cleaned_data["accion"]
            codigo = form.cleaned_data.get("codigo_muestra") or ""
            if accion == "aceptar":
                sol.estado = Solicitud.Estado.ACEPTADA
                sol.aceptado_en = timezone.now()
                if codigo:
                    sol.codigo_muestra = codigo
                messages.success(request, "Solicitud aceptada.")
            elif accion == "rechazar":
                sol.estado = Solicitud.Estado.RECHAZADA
                messages.warning(request, "Solicitud rechazada.")
            elif accion == "finalizar":
                sol.estado = Solicitud.Estado.FINALIZADA
                sol.finalizado_en = timezone.now()
                messages.success(request, "Solicitud finalizada.")
            sol.save()
            return redirect("sigmalab:detalle-solicitud", pk=sol.pk)
    else:
        form = EstadoForm()
    return render(request, "sigmalab/solicitudes/cambiar_estado.html", {"solicitud": sol, "form": form})
