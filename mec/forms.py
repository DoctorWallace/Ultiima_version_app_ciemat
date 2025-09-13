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
            # generales
            "material", "procedencia", "numero_muestras", "tratamientos",
            # dureza
            "ensayo_dureza", "dureza_carga", "dureza_huellas_filas", "dureza_huellas_columnas",
            # traccion
            "ensayo_traccion", "traccion_temperatura", "traccion_velocidad_deformacion", "traccion_diametro", "traccion_longitud_marca",
            # fatiga
            "ensayo_fatiga", "fatiga_temperatura", "fatiga_porcentaje_deformacion", "fatiga_frecuencia", "fatiga_eps_max", "fatiga_eps_min",
            # creep-fatiga
            "ensayo_creep_fatiga", "creep_temperatura", "creep_porcentaje_deformacion", "creep_frecuencia", "creep_eps_max", "creep_eps_min",
            "creep_mantenimiento_tipo", "creep_mantenimiento_en", "creep_tiempo_mantenimiento_s",
            # notas
            "observaciones",
        ]
        widgets = {
            "material": forms.TextInput(attrs={"class": "form-input", "placeholder": "Material"}),
            "procedencia": forms.TextInput(attrs={"class": "form-input", "placeholder": "Procedencia"}),
            "numero_muestras": forms.NumberInput(attrs={"class": "form-input", "min": 1}),
            "tratamientos": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "Tratamientos"}),

            "ensayo_dureza": forms.CheckboxInput(),
            "dureza_carga": forms.TextInput(attrs={"class": "form-input", "placeholder": "Carga"}),
            "dureza_huellas_filas": forms.Select(choices=[(i, i) for i in range(1, 21)], attrs={"class": "form-input"}),
            "dureza_huellas_columnas": forms.Select(choices=[(i, i) for i in range(1, 21)], attrs={"class": "form-input"}),

            "ensayo_traccion": forms.CheckboxInput(),
            "traccion_temperatura": forms.Textarea(attrs={"class": "form-input", "rows": 2, "placeholder": "Lista de temperaturas"}),
            "traccion_velocidad_deformacion": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "traccion_diametro": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "traccion_longitud_marca": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),

            "ensayo_fatiga": forms.CheckboxInput(),
            "fatiga_temperatura": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "fatiga_porcentaje_deformacion": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "fatiga_frecuencia": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "fatiga_eps_max": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "fatiga_eps_min": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),

            "ensayo_creep_fatiga": forms.CheckboxInput(),
            "creep_temperatura": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "creep_porcentaje_deformacion": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "creep_frecuencia": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "creep_eps_max": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "creep_eps_min": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),
            "creep_mantenimiento_tipo": forms.TextInput(attrs={"class": "form-input", "placeholder": "carga/deformacion"}),
            "creep_mantenimiento_en": forms.TextInput(attrs={"class": "form-input", "placeholder": "maxima/minima"}),
            "creep_tiempo_mantenimiento_s": forms.NumberInput(attrs={"class": "form-input", "step": "any"}),

            "observaciones": forms.Textarea(attrs={"class": "form-input", "rows": 4, "placeholder": "Anotaciones"}),
        }

