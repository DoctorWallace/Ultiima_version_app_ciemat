# accounts/views.py
from urllib.parse import quote as urlquote

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from urllib.parse import quote as urlquote
from django.shortcuts import redirect
from django.urls import reverse

# --- Router de login (elige ICTS o DTF según 'next') ---
# accounts/views.py (solo el router; deja el resto como lo tienes)


def login_router(request):
    nxt = request.GET.get("next") or request.POST.get("next") or ""
    ref = request.META.get("HTTP_REFERER", "") or ""

    # 1) Si hay 'next', decide por prefijo
    if nxt.startswith("/icts/"):
        return redirect(f"{reverse('accounts:login_icts')}?next={urlquote(nxt)}")
    if nxt.startswith("/dtf/") or nxt.startswith("/sigmalab/"):
        return redirect(f"{reverse('accounts:login_dtf')}?next={urlquote(nxt)}")

    # 2) Sin 'next': decide por el referer (desde qué portal venías)
    if "/dtf" in ref or "/sigmalab" in ref:
        return redirect(reverse('accounts:login_dtf'))

    # 3) Por defecto, ICTS
    return redirect(reverse("accounts:login_icts"))


# --- Login DTF ---
class LoginDTF(LoginView):
    template_name = "accounts/login_dtf.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session["module"] = "dtf"
        return response

    def get_success_url(self):
        return (
            self.request.POST.get("next")
            or self.request.GET.get("next")
            or reverse("dtf:dashboard")
        )

# --- Registro DTF básico (opcional) ---
def register_dtf(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                g = Group.objects.get(name="Usuarios Σ-LAB")
                user.groups.add(g)
            except Group.DoesNotExist:
                pass
            messages.success(request, "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
            return redirect("accounts:login_dtf")
    else:
        form = UserCreationForm()
    return render(request, "accounts/register_dtf.html", {"form": form})

# --- Logout común ---
@require_http_methods(["GET", "POST"])
@never_cache
def logout_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    module = request.GET.get("module") or request.POST.get("module") or request.session.get("module")
    logout(request)
    if next_url:
        return redirect(next_url)
    if module == "dtf":
        try:
            return redirect("dtf:dashboard")
        except Exception:
            return redirect("/dtf/")
    else:
        try:
            return redirect("icts:dashboard")
        except Exception:
            return redirect("/")
