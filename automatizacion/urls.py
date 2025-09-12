from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("portal.urls")),
    path("dtf/", include(("dtf.urls", "dtf"), namespace="dtf")),
    path("dtf/lab/", include(("sigmalab.urls", "sigmalab"), namespace="sigmalab")),
    # path("cuentas/", include(("accounts.urls", "accounts"), namespace="accounts")),#
    path("icts/", include(("icts.urls", "icts"), namespace="icts")),
    path('accounts/', include('accounts.urls')),    # ← AÑADIR
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
