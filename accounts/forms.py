from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


DEPARTAMENTOS_CIEMAT = (
    ("LNF", "Laboratorio Nacional de Fusión"),
    ("ENERGIA", "Departamento de Energía"),
    ("MEDIO_AMBIENTE", "Departamento de Medio Ambiente"),
    ("TECNOLOGIA", "Departamento de Tecnología"),
    ("INV_BASICA", "Departamento de Investigación Básica"),
    ("INNOV_BIOMED", "Unidad de Innovación Biomédica"),
    ("FISION", "Unidad de Fisión Nuclear"),
)


User = get_user_model()


class DTFRegisterForm(UserCreationForm):
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    email = forms.EmailField(label="Correo electrónico")
    first_name = forms.CharField(max_length=150, label="Nombre")
    last_name = forms.CharField(max_length=150, label="Apellidos")

    # Datos internos (solo si email @ciemat.es)
    departamento = forms.ChoiceField(
        choices=(("", "Seleccione departamento"),) + DEPARTAMENTOS_CIEMAT,
        required=False,
        label="Departamento/Unidad",
    )
    matricula = forms.CharField(max_length=50, required=False, label="Matrícula")
    telefono_interno = forms.CharField(max_length=20, required=False, label="Teléfono interno")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").lower().strip()
        is_ciemat = email.endswith("@ciemat.es")
        if is_ciemat:
            # Si es CIEMAT, obliga a completar los campos internos
            if not cleaned.get("departamento"):
                self.add_error("departamento", "Selecciona un departamento")
            if not cleaned.get("matricula"):
                self.add_error("matricula", "Indica la matrícula")
            if not cleaned.get("telefono_interno"):
                self.add_error("telefono_interno", "Indica el teléfono interno")
        return cleaned

