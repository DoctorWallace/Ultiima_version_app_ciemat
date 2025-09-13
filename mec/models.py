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
    muestras = models.ManyToManyField(MecSample, blank=True)

    # Selección de equipos (pueden ser ambos)
    equipo_durometro = models.BooleanField(default=False)
    equipo_maquina = models.BooleanField(default=False)

    # Parámetros durometro
    durometro_carga = models.CharField(max_length=50, blank=True)
    durometro_huellas_filas = models.IntegerField(null=True, blank=True)
    durometro_huellas_columnas = models.IntegerField(null=True, blank=True)
    durometro_posicion = models.CharField(max_length=200, blank=True)

    # Parámetros máquina de ensayos
    TIPO_ENSAYO = (
        ("traccion", "Tracción"),
        ("fatiga", "Fatiga"),
        ("creep-fatiga", "Creep-Fatiga"),
    )
    maquina_tipo = models.CharField(max_length=20, choices=TIPO_ENSAYO, blank=True)

    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]

    def __str__(self):
        return f"MEC#{self.pk or '-'} – {self.solicitante} – {self.estado}"
