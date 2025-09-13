# dtf/views_public.py
from django.views.generic import TemplateView
from django.shortcuts import redirect, render


class DTFHomeView(TemplateView):
    template_name = "dtf/home.html"

    def dispatch(self, request, *args, **kwargs):
        # Muestra la portada tanto si estás autenticado como si no, para evitar bucles
        return super().dispatch(request, *args, **kwargs)


LAB_LABELS = {
    "lab": {
        "name": "S-LAB",
        "logo": "/media/Logos/sigma_lab.png",
        "email": "slab@example.com",
    },
    "mec": {
        "name": "S-MEC",
        "logo": "/media/Logos/sigma_mec.png",
        "email": "smec@example.com",
    },
    "sims-implant": {
        "name": "S-SIMS·Implant",
        "logo": "/media/Logos/logo_sigma_imp_sims.png",
        "email": "sims-implant@example.com",
    },
    "dp": {
        "name": "S-D&P",
        "logo": "/media/Logos/sigma_DP.png",
        "email": "s-dp@example.com",
    },
}


def lab_info(request, slug):
    info = LAB_LABELS.get(slug)
    if not info:
        return render(request, "dtf/under_construction.html", {"slug": slug})
    return render(request, "dtf/lab_info.html", {"lab": info, "slug": slug})
