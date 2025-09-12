# accounts/views_login.py
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

@method_decorator(never_cache, name="dispatch")
class LoginICTS(LoginView):
    template_name = "accounts/login_icts.html"
    redirect_authenticated_user = False  # evita bucles si hay sesión “fantasma”

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["module"] = "icts"
        return response

    def get_success_url(self):
        # respeta ?next=...; si no, al dashboard de ICTS
        return self.request.GET.get("next") or reverse("icts:dashboard")
