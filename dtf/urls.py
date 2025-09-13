# dtf/urls.py
from django.urls import path, include
from .views_public import DTFHomeView, lab_info

app_name = "dtf"

urlpatterns = [
    path("", DTFHomeView.as_view(), name="dashboard"),
    # S-LAB bajo /dtf/lab/ con namespace "sigmalab"
    path("lab/", include(("sigmalab.urls", "sigmalab"), namespace="sigmalab")),
    # S-MEC bajo /dtf/mec/ con namespace "mec"
    path("mec/", include(("mec.urls", "mec"), namespace="mec")),
    # Info pública de labs (pre-login)
    path("labs/<slug:slug>/", lab_info, name="lab_info"),
]
