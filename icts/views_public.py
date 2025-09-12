# icts/views_public.py
from django.views.generic import TemplateView

class ICTSHomeView(TemplateView):
    template_name = "icts/home.html"
