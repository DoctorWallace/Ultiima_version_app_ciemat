# icts/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import AccessProposal, Participant, ICTSUserProfile, ProposalAttachment, ProposalReview
from django.core.exceptions import ValidationError

User = get_user_model()


# -----------------------------
# Formularios de PROPUESTA ICTS
# -----------------------------
class AccessProposalForm(forms.ModelForm):
    class Meta:
        model = AccessProposal
        fields = [
            "title", "scope", "facilities",
            "is_new_request", "previous_access", "access_code",
            "applicant_is_different", "organization", "contact_person", "email", "phone",
            "project_name", "project_type", "funding_source", "start_year", "end_year",
            "previous_experiments", "references",
            "facility_sem", "facility_sem_fib", "facility_imp", "facility_sims",
            "facility_confocal", "facility_vdg", "facility_profilometer"
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your project title"}),
            "scope": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Brief description of your project"}),
            "facilities": forms.SelectMultiple(attrs={"class": "form-select"}),
            "organization": forms.TextInput(attrs={"class": "form-control", "placeholder": "Center/Institution"}),
            "contact_person": forms.TextInput(attrs={"class": "form-control", "placeholder": "Contact person name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contact@example.com"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"}),
            "project_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Project name"}),
            "project_type": forms.TextInput(attrs={"class": "form-control", "placeholder": "International, European, National, Regional"}),
            "funding_source": forms.TextInput(attrs={"class": "form-control", "placeholder": "Funding source"}),
            "start_year": forms.NumberInput(attrs={"class": "form-control", "placeholder": "2024"}),
            "end_year": forms.NumberInput(attrs={"class": "form-control", "placeholder": "2025"}),
            "previous_experiments": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "Describe previous experiments"}),
            "references": forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": "References and citations"}),
        }


ParticipantFormSet = inlineformset_factory(
    parent_model=AccessProposal,
    model=Participant,
    fields=["name", "center", "address"],
    widgets={
        "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
        "center": forms.TextInput(attrs={"class": "form-control", "placeholder": "Center/Institution"}),
        "address": forms.Textarea(attrs={"class": "form-control", "rows": 2, "placeholder": "Address"}),
    },
    extra=1,
    can_delete=True,
)

# Validación de adjuntos (tamaño y tipo)
class ProposalAttachmentForm(forms.ModelForm):
    class Meta:
        model = ProposalAttachment
        fields = ["name", "file"]

    def clean_file(self):
        f = self.cleaned_data.get("file")
        if not f:
            return f
        max_mb = 10
        if getattr(f, "size", 0) > max_mb * 1024 * 1024:
            raise forms.ValidationError(f"El archivo supera {max_mb} MB.")

        import os
        ext = os.path.splitext(f.name)[1].lower()
        allowed_exts = {
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".png", ".jpg", ".jpeg"
        }
        if ext not in allowed_exts:
            raise forms.ValidationError("Tipo de archivo no permitido.")

        ctype = getattr(f, "content_type", "") or ""
        allowed_ctypes = {
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "image/png",
            "image/jpeg",
        }
        if ctype and ctype not in allowed_ctypes:
            raise forms.ValidationError("Tipo de contenido no permitido.")
        return f

AttachmentFormSet = inlineformset_factory(
    parent_model=AccessProposal,
    model=ProposalAttachment,
    form=ProposalAttachmentForm,
    fields=["name", "file"],
    widgets={
        "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Document name"}),
        "file": forms.FileInput(attrs={"class": "form-control"}),
    },
    extra=1,
    can_delete=True,
)


# -----------------------------
# Formulario de REGISTRO ICTS
# -----------------------------
class RegistrationICTSForm(UserCreationForm):
    # Campos “de acceso”
    username = forms.CharField(label="Usuario", max_length=150)
    email = forms.EmailField(label="Email")

    # Campos “personales”
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellidos", max_length=150)

    # Campos “perfil ICTS”
    institution = forms.CharField(label="Center", max_length=150, required=False)  # ← etiqueta visible “Center”
    phone = forms.CharField(label="Teléfono", max_length=30, required=False)
    address = forms.CharField(
        label="Dirección",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )

    accept_terms = forms.BooleanField(
        label="He leído y acepto las condiciones de uso y protección de datos.",
        required=True,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username", "email",
            "first_name", "last_name",
            "password1", "password2",
            "institution", "phone", "address", "accept_terms",
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Campos a los que SÍ queremos añadir la clase Bootstrap
        autostyle = [
            "username", "email", "first_name", "last_name",
            "institution", "phone", "address", "password1", "password2",
        ]
        for name in autostyle:
            if name in self.fields:
                self.fields[name].widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        # Usuario inactivo hasta validación manual
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.is_active = False

        if commit:
            user.save()

            # Guardamos institution → en el campo real 'center'
            ICTSUserProfile.objects.create(
                user=user,
                center=self.cleaned_data.get("institution", "").strip(),
                phone=self.cleaned_data.get("phone", "").strip(),
                address=self.cleaned_data.get("address", "").strip(),
                validated=False,
            )

            group, _ = Group.objects.get_or_create(name="icts_users")
            user.groups.add(group)

        return user


# -----------------------------
# Formulario de REVISIÓN
# -----------------------------
class ProposalReviewForm(forms.ModelForm):
    class Meta:
        model = ProposalReview
        fields = [
            "feasibility_ok", 
            "score_scientific_quality", 
            "score_need_infrastructure", 
            "score_industrial_potential",
            "comments", 
            "decision"
        ]
        widgets = {
            "feasibility_ok": forms.RadioSelect(choices=[(True, "Sí, es viable"), (False, "No es viable")]),
            "score_scientific_quality": forms.Select(choices=[("", "Selecciona una puntuación")] + [(i, f"{i} - {'Muy baja' if i==1 else 'Baja' if i==2 else 'Media' if i==3 else 'Alta' if i==4 else 'Excelente'}") for i in range(1, 6)]),
            "score_need_infrastructure": forms.Select(choices=[("", "Selecciona una puntuación")] + [(i, f"{i} - {'No necesita' if i==1 else 'Necesidad baja' if i==2 else 'Necesidad media' if i==3 else 'Necesidad alta' if i==4 else 'Crítica'}") for i in range(1, 6)]),
            "score_industrial_potential": forms.Select(choices=[("", "Selecciona una puntuación")] + [(i, f"{i} - {'Sin interés' if i==1 else 'Bajo interés' if i==2 else 'Interés medio' if i==3 else 'Alto interés' if i==4 else 'Muy alto interés'}") for i in range(1, 6)]),
            "comments": forms.Textarea(attrs={"rows": 6, "class": "form-control", "placeholder": "Proporciona comentarios detallados sobre tu evaluación..."}),
            "decision": forms.Select(choices=[
                ("", "Selecciona tu recomendación"),
                ("approve", "✅ Aprobar - La propuesta cumple con los criterios"),
                ("request_changes", "🔄 Solicitar cambios - Necesita modificaciones menores"),
                ("reject", "❌ Rechazar - No cumple con los criterios")
            ])
        } 
