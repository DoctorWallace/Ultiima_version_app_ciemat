# icts/views.py
from django.contrib import messages
from django.http import HttpResponseForbidden  # <-- añade esto
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import FormView
from django.db.models import Count, Q, Avg
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta
from django.views.decorators.cache import never_cache
from .forms import AccessProposalForm, ParticipantFormSet, AttachmentFormSet, ProposalReviewForm, RegistrationICTSForm
from django.shortcuts import render
from django.db.models import Exists, OuterRef

from .models import AccessProposal, ProposalReview
from django.contrib.auth.decorators import login_required, user_passes_test

def is_icts_user(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name__iexact="icts_users").exists()
        or user.groups.filter(name__iexact="revisores").exists()
        or user.groups.filter(name__iexact="responsables").exists()
        or user.groups.filter(name__iexact="managers").exists()
    )

def is_reviewer(user):
    return user.is_superuser or user.groups.filter(name__iexact="revisores").exists()

def is_responsable(user):
    return user.is_superuser or user.groups.filter(name__iexact="responsables").exists()

def is_manager(user):
    return user.is_superuser or user.groups.filter(name__iexact="managers").exists()

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_icts_user)
@never_cache
def dashboard(request):
    if is_manager(request.user):
        return redirect("icts:manager_dashboard")
    if is_responsable(request.user):
        return redirect("icts:responsable_dashboard")
    if is_reviewer(request.user):
        return redirect("icts:reviewer_dashboard_new")
    return redirect("icts:user_dashboard")




@login_required
def icts_user_dashboard(request):
    """
    Panel del usuario: agrupa sus propuestas por estado.
    Filtra por applicant (no owner).
    """
    qs = (
        AccessProposal.objects
        .filter(applicant=request.user)      # <- aquí está la clave
        .order_by("-created_at", "-id")
    )

    reviewed_qs = ProposalReview.objects.filter(
        proposal=OuterRef("pk"),
        decision__in=["approve", "reject", "request_changes"]
    )
    evaluated = qs.annotate(has_review=Exists(reviewed_qs)).filter(has_review=True)

    drafts = qs.filter(status="draft")
    submitted = qs.exclude(pk__in=evaluated.values("pk")).exclude(pk__in=drafts.values("pk"))

    return render(request, "icts/user_dashboard.html", {
        "drafts": drafts,
        "submitted": submitted,
        "evaluated": evaluated,
    })

# --- Registro ICTS ---
class RegisterICTSView(FormView):
    template_name = "icts/register.html"
    form_class = RegistrationICTSForm
    success_url = reverse_lazy("accounts:login_icts")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Tu cuenta ha sido registrada. Un responsable la revisará en un máximo de 48 horas.")
        return super().form_valid(form)

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_icts_user)
@never_cache
def my_proposals(request):
    qs = AccessProposal.objects.filter(applicant=request.user).order_by("-created_at")
    state = request.GET.get("state")
    if state in {"draft", "submitted", "accepted", "rejected"}:
        qs = qs.filter(status=state)
    return render(request, "icts/my_proposals.html", {"proposals": qs, "state": state})

from django.contrib.auth.decorators import login_required, user_passes_test

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_icts_user)
def proposal_create(request):
    if request.method == "POST":
        form = AccessProposalForm(request.POST)
        formset = ParticipantFormSet(request.POST)  # alias simple
        attachment_formset = AttachmentFormSet(request.POST, request.FILES)

        # Si no se renderiza el formset de adjuntos, no lo hacemos bloquear.
        # Detectamos la management form con el prefijo real del formset
        has_attach_mgmt = f"{attachment_formset.prefix}-TOTAL_FORMS" in request.POST

        if form.is_valid() and formset.is_valid() and (attachment_formset.is_valid() if has_attach_mgmt else True):
            obj = form.save(commit=False)
            obj.applicant = request.user
            if not obj.applicant_is_different:
                obj.contact_person = request.user.get_full_name() or request.user.username
                obj.email = request.user.email
                if hasattr(request.user, "icts_profile") and request.user.icts_profile:
                    obj.organization = request.user.icts_profile.center
            obj.save()
            form.save_m2m()

            formset.instance = obj
            formset.save()

            if has_attach_mgmt:
                attachment_formset.instance = obj
                attachment_formset.save()

            messages.success(request, "Propuesta creada como borrador.")
            return redirect("icts:proposal_detail", pk=obj.pk)
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = AccessProposalForm()
        formset = ParticipantFormSet()
        attachment_formset = AttachmentFormSet()

    return render(request, "icts/proposal_form.html", {
        "form": form,
        "formset": formset,                              # ← nombre coherente con la plantilla
        "attachment_formset": attachment_formset,
        "editing": False,
    })

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_icts_user)
@never_cache
def proposal_detail(request, pk):
    obj = get_object_or_404(AccessProposal, pk=pk)
    if (obj.applicant != request.user) and not (is_reviewer(request.user) or is_responsable(request.user)):
        messages.error(request, "No tienes permiso para ver esa propuesta.")
        return redirect("icts:dashboard")

    reviews = obj.reviews.select_related("reviewer").all()
    can_decide = is_responsable(request.user) and obj.status == "submitted"

    return render(
        request,
        "icts/proposal_detail.html",
        {"obj": obj, "reviews": reviews, "can_decide": can_decide}
    )



@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_icts_user)
@never_cache
def proposal_edit(request, pk):
    obj = get_object_or_404(AccessProposal, pk=pk, applicant=request.user)
    if obj.status != "draft":
        messages.error(request, "Solo se pueden editar propuestas en borrador.")
        return redirect("icts:proposal_detail", pk=obj.pk)

    if request.method == "POST":
        form = AccessProposalForm(request.POST, instance=obj)
        formset = ParticipantFormSet(request.POST, instance=obj)
        # Edición sin adjuntos (se añadirá en el siguiente paso)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Borrador actualizado.")
            return redirect("icts:proposal_detail", pk=obj.pk)
    else:
        form = AccessProposalForm(instance=obj)
        formset = ParticipantFormSet(instance=obj)

    return render(request, "icts/proposal_form.html", {"form": form, "formset": formset, "editing": True})

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_icts_user)
@never_cache
def proposal_submit(request, pk):
    """Pasa de 'draft' a 'submitted' y crea tareas de revisión para TODOS los revisores."""
    obj = get_object_or_404(AccessProposal, pk=pk, applicant=request.user)
    if obj.status != "draft":
        messages.error(request, "Solo se pueden enviar propuestas en borrador.")
        return redirect("icts:proposal_detail", pk=obj.pk)

    # Cambia estado
    obj.status = "submitted"
    obj.save(update_fields=["status"])

    # Asigna revisores: crea una ProposalReview 'pending' por cada miembro del grupo 'revisores'
    from django.contrib.auth.models import Group
    reviewers = Group.objects.filter(name__iexact="revisores").first()
    if reviewers:
        for user in reviewers.user_set.all().distinct():
            ProposalReview.objects.get_or_create(proposal=obj, reviewer=user)

    messages.success(request, "Propuesta enviada a revisión.")
    return redirect("icts:proposal_detail", pk=obj.pk)



@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_reviewer)
@never_cache
def reviewer_inbox(request):
    pending = AccessProposal.objects.filter(status="submitted").order_by("-created_at")
    mine = ProposalReview.objects.filter(reviewer=request.user).select_related("proposal")
    return render(request, "icts/reviewer_inbox.html", {"pending": pending, "mine": mine})

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_reviewer)
@never_cache
def reviewer_dashboard_new(request):
    """Dashboard mejorado del revisor con estadísticas y plazos"""
    from datetime import datetime, timedelta
    
    # Estadísticas básicas
    pending_reviews = ProposalReview.objects.filter(
        reviewer=request.user,
        decision='pending'
    ).select_related('proposal')
    
    completed_reviews = ProposalReview.objects.filter(
        reviewer=request.user,
        decision__in=['approve', 'reject', 'request_changes']
    )
    
    # Contadores
    pending_count = pending_reviews.count()
    completed_count = completed_reviews.count()
    approved_count = completed_reviews.filter(decision='approve').count()
    rejected_count = completed_reviews.filter(decision='reject').count()
    
    # Revisiones pendientes con información de días
    pending_with_days = []
    for review in pending_reviews:
        days_pending = (datetime.now().date() - review.proposal.created_at.date()).days
        is_urgent = days_pending > 7  # Más de 7 días es urgente
        pending_with_days.append({
            'review': review,
            'days_pending': days_pending,
            'is_urgent': is_urgent
        })
    
    urgent_count = sum(1 for item in pending_with_days if item['is_urgent'])
    
    # Revisiones recientes (últimas 5)
    recent_reviews = completed_reviews.order_by('-updated_at')[:5]
    
    context = {
        'pending_count': pending_count,
        'completed_count': completed_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'urgent_count': urgent_count,
        'pending_reviews': pending_with_days,
        'recent_reviews': recent_reviews,
    }
    
    return render(request, "icts/reviewer_dashboard_new.html", context)

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_reviewer)
@never_cache
def review_history(request):
    """Historial de evaluaciones del revisor con filtros"""
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Obtener todas las evaluaciones del revisor
    reviews = ProposalReview.objects.filter(
        reviewer=request.user
    ).select_related('proposal', 'proposal__applicant').order_by('-updated_at')
    
    # Aplicar filtros
    decision = request.GET.get('decision')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if decision:
        reviews = reviews.filter(decision=decision)
    
    if date_from:
        reviews = reviews.filter(updated_at__date__gte=date_from)
    
    if date_to:
        reviews = reviews.filter(updated_at__date__lte=date_to)
    
    if search:
        reviews = reviews.filter(
            Q(proposal__title__icontains=search) |
            Q(proposal__applicant__username__icontains=search) |
            Q(proposal__applicant__first_name__icontains=search) |
            Q(proposal__applicant__last_name__icontains=search)
        )
    
    # Paginación
    paginator = Paginator(reviews, 10)  # 10 evaluaciones por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reviews': page_obj,
        'total_reviews': reviews.count(),
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, "icts/review_history.html", context)

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_responsable)
@never_cache
def responsable_dashboard(request):
    """Dashboard del responsable con semáforo de revisiones"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Estadísticas básicas
    stats = {
        "total": AccessProposal.objects.count(),
        "draft": AccessProposal.objects.filter(status="draft").count(),
        "submitted": AccessProposal.objects.filter(status="submitted").count(),
        "under_review": AccessProposal.objects.filter(status="submitted").count(),
        "accepted": AccessProposal.objects.filter(status="accepted").count(),
        "rejected": AccessProposal.objects.filter(status="rejected").count(),
    }
    
    # Semáforo de revisiones
    proposals_with_reviews = AccessProposal.objects.annotate(
        review_count=Count('reviews')
    ).filter(status="submitted")
    
    review_buckets = {
        "rojo_0": proposals_with_reviews.filter(review_count=0).count(),
        "amarillo_1_3": proposals_with_reviews.filter(review_count__gte=1, review_count__lte=3).count(),
        "verde_4mas": proposals_with_reviews.filter(review_count__gte=4).count(),
    }
    
    # Propuestas pendientes de decisión (con al menos 4 revisiones)
    pendientes = AccessProposal.objects.annotate(
        review_count=Count('reviews'),
        reviewers_done=Count('reviews', filter=Q(reviews__decision__in=['approve', 'reject', 'request_changes']))
    ).filter(
        status="submitted",
        review_count__gte=4
    ).order_by('-created_at')[:20]
    
    # Últimas decisiones
    ultimas = AccessProposal.objects.filter(
        status__in=['accepted', 'rejected']
    ).order_by('-created_at')[:10]
    
    # Estadísticas de revisores
    reviewer_stats = []
    reviewers = User.objects.filter(groups__name="revisores")
    for reviewer in reviewers:
        completed = ProposalReview.objects.filter(
            reviewer=reviewer,
            decision__in=['approve', 'reject', 'request_changes']
        ).count()
        pending = ProposalReview.objects.filter(
            reviewer=reviewer,
            decision="pending"
        ).count()
        last_review = ProposalReview.objects.filter(
            reviewer=reviewer
        ).order_by('-updated_at').first()
        
        reviewer_stats.append({
            "user": reviewer,
            "completed_reviews": completed,
            "pending_reviews": pending,
            "last_review": last_review.updated_at if last_review else None,
        })
    
    return render(request, "icts/responsable_dashboard.html", {
        "stats": stats,
        "review_buckets": review_buckets,
        "pendientes": pendientes,
        "ultimas": ultimas,
        "reviewer_stats": reviewer_stats,
    })


@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_manager)
@never_cache
def manager_dashboard(request):
    """Dashboard avanzado para managers con estadísticas detalladas"""
    from django.contrib.auth import get_user_model
    from django.db.models import Count, Avg, Q
    
    User = get_user_model()
    
    # Estadísticas básicas
    total_proposals = AccessProposal.objects.count()
    draft_proposals = AccessProposal.objects.filter(status="draft").count()
    submitted_proposals = AccessProposal.objects.filter(status="submitted").count()
    approved_proposals = AccessProposal.objects.filter(status="accepted").count()
    rejected_proposals = AccessProposal.objects.filter(status="rejected").count()
    
    # Cálculo de tasas
    total_decided = approved_proposals + rejected_proposals
    approval_rate = round((approved_proposals / total_decided * 100) if total_decided > 0 else 0, 1)
    rejection_rate = round((rejected_proposals / total_decided * 100) if total_decided > 0 else 0, 1)
    
    # Estadísticas de revisión
    total_reviews = ProposalReview.objects.count()
    pending_reviews = ProposalReview.objects.filter(decision="pending").count()
    completed_reviews = ProposalReview.objects.exclude(decision="pending").count()
    
    # Promedio de revisiones por propuesta
    proposals_with_reviews = AccessProposal.objects.annotate(
        review_count=Count('reviews')
    ).filter(review_count__gt=0)
    avg_reviews_per_proposal = round(
        proposals_with_reviews.aggregate(avg=Avg('review_count'))['avg'] or 0, 1
    )
    
    # Propuestas que necesitan más revisiones
    proposals_need_reviews = AccessProposal.objects.annotate(
        review_count=Count('reviews')
    ).filter(status="submitted", review_count__lt=4).count()
    
    # Estadísticas de usuarios
    total_users = User.objects.count()
    active_researchers = User.objects.filter(is_active=True, groups__name="icts_users").count()
    reviewers_count = User.objects.filter(groups__name="revisores").count()
    responsables_count = User.objects.filter(groups__name="responsables").count()
    
    # Actividad reciente
    thirty_days_ago = timezone.now() - timedelta(days=30)
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    recent_proposals = AccessProposal.objects.filter(created_at__gte=thirty_days_ago).count()
    weekly_proposals = AccessProposal.objects.filter(created_at__gte=seven_days_ago).count()
    recent_submissions = AccessProposal.objects.filter(
        status="submitted", 
        created_at__gte=thirty_days_ago
    ).count()
    
    # Tiempo promedio de revisión
    completed_reviews_with_time = ProposalReview.objects.filter(
        decision__in=['approve', 'reject', 'request_changes']
    ).exclude(updated_at__isnull=True)
    
    avg_review_time_days = 0
    if completed_reviews_with_time.exists():
        # Calcular tiempo promedio (simplificado)
        avg_review_time_days = 7  # Placeholder - implementar cálculo real
    
    # Estadísticas por técnica (simplificado)
    technique_stats = [
        {"name": "SEM/EDX", "count": 15, "percentage": 30},
        {"name": "FIB", "count": 12, "percentage": 24},
        {"name": "SIMS", "count": 10, "percentage": 20},
        {"name": "Confocal", "count": 8, "percentage": 16},
        {"name": "Ion Implanter", "count": 5, "percentage": 10},
    ]
    
    # Estadísticas por año
    yearly_stats = [
        {"year": "2024", "count": 25, "percentage": 50},
        {"year": "2023", "count": 15, "percentage": 30},
        {"year": "2022", "count": 10, "percentage": 20},
    ]
    
    # Top técnicas
    top_techniques = technique_stats[:3]
    
    return render(request, "icts/manager_dashboard.html", {
        "total_proposals": total_proposals,
        "draft_proposals": draft_proposals,
        "submitted_proposals": submitted_proposals,
        "approved_proposals": approved_proposals,
        "rejected_proposals": rejected_proposals,
        "approval_rate": approval_rate,
        "rejection_rate": rejection_rate,
        "total_reviews": total_reviews,
        "pending_reviews": pending_reviews,
        "completed_reviews": completed_reviews,
        "avg_reviews_per_proposal": avg_reviews_per_proposal,
        "proposals_need_reviews": proposals_need_reviews,
        "total_users": total_users,
        "active_researchers": active_researchers,
        "reviewers_count": reviewers_count,
        "responsables_count": responsables_count,
        "recent_proposals": recent_proposals,
        "weekly_proposals": weekly_proposals,
        "recent_submissions": recent_submissions,
        "avg_review_time_days": avg_review_time_days,
        "technique_stats": technique_stats,
        "yearly_stats": yearly_stats,
        "top_techniques": top_techniques,
    })


@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_reviewer)
@never_cache
def review_start(request, pk):
    obj = get_object_or_404(AccessProposal, pk=pk)
    # Asegura que exista el registro de review para este revisor
    review, _ = ProposalReview.objects.get_or_create(proposal=obj, reviewer=request.user)

    if request.method == "POST":
        form = ProposalReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Revisión guardada.")
            return redirect("icts:reviewer_inbox")
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = ProposalReviewForm(instance=review)

    return render(request, "icts/review_form.html", {
        "proposal": obj, 
        "form": form,
        "review": review
    })

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_responsable)
@never_cache
def proposal_decide(request, pk):
    obj = get_object_or_404(AccessProposal, pk=pk)
    if request.method == "POST":
        decision = request.POST.get("final_decision")
        if decision not in {"accepted", "rejected"}:
            messages.error(request, "Selección inválida.")
            return redirect("icts:proposal_detail", pk=obj.pk)
        obj.status = decision
        obj.save(update_fields=["status"])
        messages.success(request, f"Decisión final registrada: {obj.get_status_display()}.")
        return redirect("icts:proposal_detail", pk=obj.pk)
    return HttpResponseForbidden("Método no permitido")


# ========= GESTIÓN DE USUARIOS =========

@login_required(login_url="/accounts/login/icts/")
@user_passes_test(lambda u: is_responsable(u) or is_manager(u))
@never_cache
def pending_users(request):
    """Vista para mostrar usuarios pendientes de validación"""
    from django.contrib.auth import get_user_model
    from .models import ICTSUserProfile
    
    User = get_user_model()
    
    # Usuarios inactivos con perfil ICTS
    pending_users = User.objects.filter(
        is_active=False,
        icts_profile__isnull=False
    ).select_related('icts_profile').order_by('-date_joined')
    
    # Estadísticas
    pending_count = pending_users.count()
    validated_today = User.objects.filter(
        is_active=True,
        date_joined__date=timezone.now().date()
    ).count()
    total_users = User.objects.count()
    
    return render(request, "icts/pending_users.html", {
        "pending_users": pending_users,
        "pending_count": pending_count,
        "validated_today": validated_today,
        "total_users": total_users,
    })


@login_required(login_url="/accounts/login/icts/")
@user_passes_test(is_manager)
@never_cache
def users_admin(request):
    """Vista para administración completa de usuarios"""
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    
    User = get_user_model()
    
    # Parámetros de ordenación
    sort = request.GET.get('sort', 'joined')
    direction = request.GET.get('dir', 'desc')
    
    # Construir ordenación
    order_field = {
        'name': 'first_name',
        'email': 'email',
        'joined': 'date_joined',
        'last_login': 'last_login',
        'active': 'is_active',
        'staff': 'is_staff',
    }.get(sort, 'date_joined')
    
    if direction == 'asc':
        order_field = order_field
    else:
        order_field = f'-{order_field}'
    
    # Obtener usuarios
    users_list = User.objects.all().order_by(order_field)
    
    # Usuarios pendientes
    pending_users = User.objects.filter(
        is_active=False,
        icts_profile__isnull=False
    ).select_related('icts_profile').order_by('-date_joined')
    
    # Estadísticas
    total_users = User.objects.count()
    pending_count = pending_users.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    staff_users = User.objects.filter(is_staff=True).count()
    
    return render(request, "icts/users_admin.html", {
        "users_list": users_list,
        "pending_users": pending_users,
        "total_users": total_users,
        "pending_count": pending_count,
        "active_users": active_users,
        "inactive_users": inactive_users,
        "staff_users": staff_users,
        "sort": sort,
        "dir": direction,
    })


@login_required(login_url="/accounts/login/icts/")
@user_passes_test(lambda u: is_responsable(u) or is_manager(u))
@never_cache
def approve_user(request, user_id):
    """Aprobar un usuario pendiente"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    if user.is_active:
        messages.warning(request, "Este usuario ya está activo.")
    else:
        user.is_active = True
        user.save()
        messages.success(request, f"Usuario {user.username} ha sido aprobado y activado.")
    
    return redirect("icts:pending_users")


@login_required(login_url="/accounts/login/icts/")
@user_passes_test(lambda u: is_responsable(u) or is_manager(u))
@never_cache
def reject_user(request, user_id):
    """Rechazar un usuario pendiente"""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    username = user.username
    user.delete()
    messages.success(request, f"Usuario {username} ha sido rechazado y eliminado.")
    
    return redirect("icts:pending_users")


FACILITY_LABELS = {
    "van-der-graaff": "Van der Graaff",
    "sem-edx": "SEM/EDX",
    "fib": "FIB",
    "implantador": "Implantador",
    "sims": "SIMS",
    "confocal": "Confocal",
    "corrosion": "Corrosión",
}

def facility_info(request, slug):
    label = FACILITY_LABELS.get(slug, slug.replace("-", " ").title())
    return render(request, "icts/facility_info.html", {"facility": label, "slug": slug})

@never_cache
def proposal_evaluation(request):
    return render(request, "icts/proposal_evaluation.html")
