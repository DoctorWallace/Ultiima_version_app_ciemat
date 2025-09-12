from django.urls import path
from . import views
from . import views_requests as req  # si ya lo usabas

app_name = "sigmalab"

urlpatterns = [
    # Redirecciona al panel correcto
    path("", views.dashboard, name="dashboard"),

    # Paneles
    path("panel/tecnico/", views.panel_tecnico, name="panel-tecnico"),
    path("panel/usuario/", views.panel_usuario, name="panel-usuario"),

    # Muestras (demo)
    path("samples/", views.sample_list, name="sample-list"),
    path("samples/new/", views.sample_create, name="sample-create"),

    # Solicitudes (si las traías de labrequest/sigmalab_temp)
    path("requests/new/",  req.nueva_solicitud,   name="nueva-solicitud"),
    path("requests/mine/", req.mis_solicitudes,   name="mis-solicitudes"),
    path("requests/<int:pk>/", req.detalle_solicitud, name="detalle-solicitud"),
    path("requests/<int:pk>/avances/new/", req.nuevo_avance, name="nuevo-avance"),
    path("requests/inbox/", req.bandeja_tecnico,  name="bandeja-tecnico"),
    path("requests/all/",   req.todas_solicitudes, name="todas-solicitudes"),
    path("requests/<int:pk>/estado/", req.cambiar_estado, name="cambiar-estado"),

    # Usuarios (solo técnicos)
    path("usuarios/", views.usuarios_overview, name="usuarios-overview"),
]
