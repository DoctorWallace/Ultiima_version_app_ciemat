from django import forms
from .models import Sample
from .models import Solicitud, Avance, DiarioEntrada


class SampleForm(forms.ModelForm):
    class Meta:
        model = Sample
        fields = ["code", "title", "notes"]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-input", "placeholder": "Código único"}),
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "Título descriptivo"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "rows": 5, "placeholder": "Notas (opcional)"}),
        }


class SolicitudForm(forms.ModelForm):
    class Meta:
        model = Solicitud
        fields = [
            "material",
            "procedencia",
            "tratamiento_previo",
            "corte",
            "empastillado",
            "lijado",
            "pulido",
            "electropulido",
            "trat_quimico",
            "trat_termico",
            "requisitos_finales",
            "observaciones",
        ]
        widgets = {
            "material": forms.TextInput(attrs={"class": "form-input", "placeholder": "Material"}),
            "procedencia": forms.TextInput(attrs={"class": "form-input"}),
            "tratamiento_previo": forms.TextInput(attrs={"class": "form-input"}),
            "requisitos_finales": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
            "observaciones": forms.Textarea(attrs={"class": "form-input", "rows": 3}),
        }


class AvanceForm(forms.ModelForm):
    class Meta:
        model = Avance
        fields = ["tipo", "contenido", "adjunto", "visible_para_usuario"]
        widgets = {
            "contenido": forms.Textarea(attrs={"rows": 4, "placeholder": "Describe el avance o mensaje."}),
        }


class EstadoForm(forms.Form):
    ACCION = (
        ("aceptar", "Aceptar"),
        ("rechazar", "Rechazar"),
        ("finalizar", "Finalizar"),
    )
    accion = forms.ChoiceField(choices=ACCION)
    codigo_muestra = forms.CharField(required=False, max_length=20)


class DiarioEntradaForm(forms.ModelForm):
    class Meta:
        model = DiarioEntrada
        fields = ["fecha", "etapa", "nota"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "etapa": forms.Select(attrs={"class": "form-input"}),
            "nota": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-input",
                    "placeholder": "Anota incidencias, tareas realizadas, etc.",
                }
            ),
        }

