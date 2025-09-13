# icts/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# --- Modelos principales ICTS ---

class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class AccessProposal(models.Model):
    PROJECT_TYPE_CHOICES = [
        ("international", "International"),
        ("european", "European"),
        ("national", "National"),
        ("regional", "Regional"),
    ]
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]
    
    # Información básica
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="icts_proposals",
    )
    title = models.CharField(max_length=200)
    scope = models.TextField(blank=True)
    facilities = models.ManyToManyField(Facility, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="draft")
    user_siglas = models.CharField("Siglas usuario", max_length=10, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Campos adicionales del template de prueba
    is_new_request = models.BooleanField(default=True, help_text="Is this a new request?")
    previous_access = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Previous approved request to copy data from"
    )
    access_code = models.CharField(max_length=50, blank=True, help_text="Auto-generated access code")
    
    # Información del solicitante (cuando es diferente del usuario registrado)
    applicant_is_different = models.BooleanField(default=False)
    organization = models.CharField(max_length=200, blank=True, help_text="Center/Institution")
    contact_person = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Información del proyecto de financiación
    project_name = models.CharField(max_length=200, blank=True)
    project_type = models.CharField(
        max_length=100,
        blank=True,
        choices=PROJECT_TYPE_CHOICES,
        help_text="International, European, National, Regional",
    )
    funding_source = models.CharField(max_length=200, blank=True)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    
    # Experimentos previos y referencias
    previous_experiments = models.TextField(blank=True)
    references = models.TextField(blank=True)
    
    # Facilidades específicas (checkboxes individuales)
    facility_sem = models.BooleanField(default=False)
    facility_sem_fib = models.BooleanField(default=False)
    facility_imp = models.BooleanField(default=False)
    facility_sims = models.BooleanField(default=False)
    facility_confocal = models.BooleanField(default=False)
    facility_vdg = models.BooleanField(default=False)
    facility_profilometer = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class Participant(models.Model):
    proposal = models.ForeignKey(
        AccessProposal, on_delete=models.CASCADE, related_name="participants"
    )
    name = models.CharField(max_length=120, help_text="Full name of participant")
    center = models.CharField(max_length=200, blank=True, help_text="Center/Institution")
    address = models.TextField(blank=True, help_text="Address")

    def __str__(self):
        return f"{self.name} — {self.proposal.title}"


class ProposalReview(models.Model):
    DECISION = [
        ("pending", "Pending"),
        ("approve", "Approve"),
        ("request_changes", "Request changes"),
        ("reject", "Reject"),
    ]
    proposal = models.ForeignKey(
        AccessProposal, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="icts_reviews"
    )
    decision = models.CharField(max_length=16, choices=DECISION, default="pending")
    comments = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Campos adicionales del template de revisión
    feasibility_ok = models.BooleanField(null=True, blank=True, help_text="Is this proposal technically feasible?")
    score_scientific_quality = models.IntegerField(
        null=True, blank=True, 
        choices=[(i, i) for i in range(1, 6)],
        help_text="Scientific quality score (1-5)"
    )
    score_need_infrastructure = models.IntegerField(
        null=True, blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Need for advanced infrastructure score (1-5)"
    )
    score_industrial_potential = models.IntegerField(
        null=True, blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="Industrial potential score (1-5)"
    )

    class Meta:
        unique_together = ("proposal", "reviewer")

    def __str__(self):
        return f"Review {self.proposal_id} by {self.reviewer} -> {self.decision}"


class ProposalAttachment(models.Model):
    """Archivos adjuntos a las propuestas"""
    proposal = models.ForeignKey(
        AccessProposal, on_delete=models.CASCADE, related_name="attachments"
    )
    name = models.CharField(max_length=200, help_text="Document name")
    file = models.FileField(upload_to="proposal_attachments/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.proposal.title}"


# --- Perfil de usuario ICTS (datos adicionales del registro) ---

User = get_user_model()

class ICTSUserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="icts_profile"
    )
    center = models.CharField("Centro / Institución", max_length=150, blank=True)
    phone = models.CharField("Teléfono", max_length=30, blank=True)
    address = models.TextField("Dirección", blank=True)
    validated = models.BooleanField("Validado por responsable", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Perfil ICTS de {self.user.get_username()}"
