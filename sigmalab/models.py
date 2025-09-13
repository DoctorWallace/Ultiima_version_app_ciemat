from django.db import models
from django.conf import settings

# ========= Modelo mínimo de Muestra =========
class Sample(models.Model):
    code = models.CharField("Código", max_length=20, unique=True)
    title = models.CharField("Título", max_length=200)
    notes = models.TextField("Notas", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name="Propietario", on_delete=models.PROTECT
    )
    created_at = models.DateTimeField("Creado", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Muestra"
        verbose_name_plural = "Muestras"

    def __str__(self):
        return f"{self.code} – {self.title}"


# ========= Solicitudes (port de labrequest) =========
class Solicitud(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACEPTADA = "aceptada", "Aceptada"
        RECHAZADA = "rechazada", "Rechazada"
        EN_CURSO = "en_curso", "En curso"
        FINALIZADA = "finalizada", "Finalizada"

    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="solicitudes"
    )
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="solicitudes_asignadas",
    )

    material = models.CharField(max_length=200, blank=True)
    procedencia = models.CharField(max_length=200, blank=True)
    tratamiento_previo = models.CharField(max_length=200, blank=True)
    requisitos_finales = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)

    # Operaciones de preparación
    corte = models.BooleanField(default=False)
    empastillado = models.BooleanField(default=False)
    lijado = models.BooleanField(default=False)
    pulido = models.BooleanField(default=False)
    electropulido = models.BooleanField(default=False)
    trat_quimico = models.BooleanField(default=False)
    trat_termico = models.BooleanField(default=False)

    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    autonomo = models.BooleanField(
        default=False, help_text="Usuario validado como autónomo para esta solicitud"
    )
    codigo_muestra = models.CharField(
        max_length=20, blank=True, null=True, help_text="Se puede asignar al aceptar (p.ej. 25-001)"
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    aceptado_en = models.DateTimeField(null=True, blank=True)
    finalizado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "Solicitud"
        verbose_name_plural = "Solicitudes"

    def __str__(self):
        return f"SOL#{self.pk or '-'} – {self.solicitante} – {self.estado}"


class Avance(models.Model):
    TIPO = (("avance", "Avance"), ("nota", "Nota interna"))

    # Importante: referencia en cadena para evitar NameError por orden de clases
    solicitud = models.ForeignKey("sigmalab.Solicitud", on_delete=models.CASCADE, related_name="avances")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="avances_publicados"
    )
    tipo = models.CharField(max_length=10, choices=TIPO, default="avance")
    contenido = models.TextField()
    adjunto = models.FileField(upload_to="avances/", blank=True, null=True)
    visible_para_usuario = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["creado_en"]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.solicitud} - {self.creado_en:%Y-%m-%d %H:%M}"


class DiarioEntrada(models.Model):
    ETAPA = (
        ("corte", "Corte"),
        ("empastillado", "Empastillado"),
        ("lijado", "Lijado"),
        ("pulido", "Pulido"),
        ("electropulido", "Electropulido"),
        ("trat_quimico", "Tratamiento químico"),
        ("trat_termico", "Tratamiento térmico"),
        ("ensayo", "Ensayo máquina"),
        ("otra", "Otra"),
    )
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, related_name="diario")
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    fecha = models.DateField()
    etapa = models.CharField(max_length=20, choices=ETAPA)
    nota = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado_en"]

    def __str__(self):
        return f"Diario {self.solicitud_id} {self.fecha} {self.etapa}"

