from django.db import models
from django.conf import settings


class MecSample(models.Model):
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=100, blank=True)
    tratamientos = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.nombre}"


class MecSolicitud(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACEPTADA = "aceptada", "Aceptada"
        RECHAZADA = "rechazada", "Rechazada"
        EN_CURSO = "en_curso", "En curso"
        FINALIZADA = "finalizada", "Finalizada"

    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="mec_solicitudes")
    tecnico_responsable = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="mec_solicitudes_asignadas"
    )

    # Datos generales
    material = models.CharField(max_length=200, blank=True)
    procedencia = models.CharField(max_length=200, blank=True)
    numero_muestras = models.PositiveIntegerField(default=1)
    tratamientos = models.TextField(blank=True)

    # Ensayo de dureza
    ensayo_dureza = models.BooleanField(default=False)
    dureza_carga = models.CharField(max_length=100, blank=True)
    dureza_huellas_filas = models.PositiveIntegerField(null=True, blank=True)
    dureza_huellas_columnas = models.PositiveIntegerField(null=True, blank=True)

    # Ensayo de tracción
    ensayo_traccion = models.BooleanField(default=False)
    traccion_temperatura = models.CharField(max_length=200, blank=True, help_text="Una por muestra, separadas por coma o línea")
    traccion_velocidad_deformacion = models.FloatField(null=True, blank=True, help_text="s^-1")
    traccion_diametro = models.FloatField(null=True, blank=True)
    traccion_longitud_marca = models.FloatField(null=True, blank=True)

    # Ensayo de fatiga
    ensayo_fatiga = models.BooleanField(default=False)
    fatiga_temperatura = models.FloatField(null=True, blank=True)
    fatiga_porcentaje_deformacion = models.FloatField(null=True, blank=True)
    fatiga_frecuencia = models.FloatField(null=True, blank=True)
    fatiga_eps_max = models.FloatField(null=True, blank=True)
    fatiga_eps_min = models.FloatField(null=True, blank=True)

    # Ensayo de creep-fatiga
    ensayo_creep_fatiga = models.BooleanField(default=False)
    creep_temperatura = models.FloatField(null=True, blank=True)
    creep_porcentaje_deformacion = models.FloatField(null=True, blank=True)
    creep_frecuencia = models.FloatField(null=True, blank=True)
    creep_eps_max = models.FloatField(null=True, blank=True)
    creep_eps_min = models.FloatField(null=True, blank=True)
    creep_mantenimiento_tipo = models.CharField(max_length=20, blank=True, help_text="carga/deformacion")
    creep_mantenimiento_en = models.CharField(max_length=20, blank=True, help_text="maxima/minima")
    creep_tiempo_mantenimiento_s = models.FloatField(null=True, blank=True)

    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"MEC#{self.pk or '-'} - {self.solicitante} - {self.estado}"


class MecMuestraNombre(models.Model):
    solicitud = models.ForeignKey(MecSolicitud, on_delete=models.CASCADE, related_name="nombres")
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

