# dtf/urls.py
from django.urls import path, include
from django.views.generic import TemplateView

app_name = "dtf"

urlpatterns = [
    path("", TemplateView.as_view(template_name="dtf/home.html"), name="dashboard"),
    # Σ-LAB bajo /dtf/lab/ con namespace "sigmalab"
    path("lab/", include(("sigmalab.urls", "sigmalab"), namespace="sigmalab")),
]
