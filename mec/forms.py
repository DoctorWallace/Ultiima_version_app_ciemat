from django import forms
from .models import MecSample, MecSolicitud


class MecSampleForm(forms.ModelForm):
    class Meta:
        model = MecSample
        fields = ["nombre", "tipo", "tratamientos"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-input", "placeholder": "Nombre de la muestra"}),
            "tipo": forms.TextInput(attrs={"class": "form-input", "placeholder": "Tipo"}),
            "tratamientos": forms.Textarea(attrs={"class": "form-input", "rows": 4, "placeholder": "Tratamientos previos"}),
        }


class MecSolicitudForm(forms.ModelForm):
    class Meta:
        model = MecSolicitud
        fields = [
            "muestras",
            "equipo_durometro", "durometro_carga", "durometro_huellas_filas", "durometro_huellas_columnas", "durometro_posicion",
            "equipo_maquina", "maquina_tipo",
            "observaciones",
        ]
        widgets = {
            "muestras": forms.SelectMultiple(attrs={"class": "form-input"}),
            "equipo_durometro": forms.CheckboxInput(attrs={}),
            "durometro_carga": forms.TextInput(attrs={"class": "form-input", "placeholder": "Carga"}),
            "durometro_huellas_filas": forms.NumberInput(attrs={"class": "form-input", "min": 1}),
            "durometro_huellas_columnas": forms.NumberInput(attrs={"class": "form-input", "min": 1}),
            "durometro_posicion": forms.TextInput(attrs={"class": "form-input", "placeholder": "Posición de ensayo"}),
            "equipo_maquina": forms.CheckboxInput(attrs={}),
            "maquina_tipo": forms.Select(attrs={"class": "form-input"}, choices=MecSolicitud.TIPO_ENSAYO),
            "observaciones": forms.Textarea(attrs={"class": "form-input", "rows": 4}),
        }

