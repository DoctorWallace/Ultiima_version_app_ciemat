# mec/urls.py
from django.urls import path
from . import views

app_name = "mec"

urlpatterns = [
    path("", views.panel_usuario, name="panel_usuario"),
    path("panel/tecnico/", views.panel_tecnico_responsable, name="panel_tecnico"),
    path("muestras/nueva/", views.sample_create, name="sample_create"),
    path("solicitudes/nueva/", views.solicitud_create, name="solicitud_create"),
]
