# dtf/views_public.py
from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.conf import settings
import os


class DTFHomeView(TemplateView):
    template_name = "dtf/home.html"

    def dispatch(self, request, *args, **kwargs):
        # Si está autenticado, redirige al router de S‑LAB (elige panel por rol)
        if request.user.is_authenticated:
            from django.shortcuts import redirect
            return redirect('sigmalab:dashboard')
        return super().dispatch(request, *args, **kwargs)


LAB_LABELS = {
    "lab": {
        "name": "S-LAB",
        "logo": "/media/Logos/sigma_lab.png",
        "email": "montserrat.martin@ciemat.es",
        "responsable": "Montserrat Martín Laso",
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

    gallery_rows = []
    if slug == "lab":
        # Buscar imágenes en MEDIA_ROOT/lab con patrón Lab_(XX).jpg o variantes similares
        lab_dir = os.path.join(settings.MEDIA_ROOT, "lab")
        images = []
        try:
            if os.path.isdir(lab_dir):
                for fn in sorted(os.listdir(lab_dir)):
                    low = fn.lower()
                    if low.endswith('.jpg') and (low.startswith('lab_') or low.startswith('lab (') or low.startswith('lab')):
                        images.append(settings.MEDIA_URL.rstrip('/') + '/lab/' + fn)
        except Exception:
            images = []

        # Agrupar de 3 en 3 y calcular huecos para completar la cuadrícula
        for i in range(0, len(images), 3):
            chunk = images[i:i+3]
            filler = max(0, 3 - len(chunk))
            gallery_rows.append({
                "images": chunk,
                "filler_str": "x" * filler,  # iterar sobre string para añadir huecos
            })

    ctx = {"lab": info, "slug": slug, "gallery_rows": gallery_rows}
    return render(request, "dtf/lab_info.html", ctx)
