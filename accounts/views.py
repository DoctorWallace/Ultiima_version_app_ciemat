# accounts/views.py
from urllib.parse import quote as urlquote

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.urls import reverse

from .forms import DTFRegisterForm
from dtf.models import DTFUserProfile


# --- Router de login (elige ICTS o DTF según 'next') ---
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


# --- Registro DTF ---
def register_dtf(request):
    if request.method == "POST":
        form = DTFRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email").lower().strip()
            user.first_name = form.cleaned_data.get("first_name").strip()
            user.last_name = form.cleaned_data.get("last_name").strip()
            user.save()

            # Grupo base DTF
            try:
                g = Group.objects.get(name="usuarios_dtf")
                user.groups.add(g)
            except Group.DoesNotExist:
                pass

            # Perfil DTF
            email = user.email
            is_ciemat = email.endswith("@ciemat.es")
            DTFUserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "is_ciemat": is_ciemat,
                    "departamento": form.cleaned_data.get("departamento") or "",
                    "matricula": form.cleaned_data.get("matricula") or "",
                    "telefono_interno": form.cleaned_data.get("telefono_interno") or "",
                },
            )

            messages.success(request, "Cuenta creada correctamente. Ahora puedes iniciar sesión.")
            return redirect("accounts:login_dtf")
    else:
        form = DTFRegisterForm()
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

