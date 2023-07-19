from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic.base import RedirectView

urlpatterns = (
    [
        path("", include("core.urls")),
        #path("", include("django.contrib.auth.urls")),
        path('oidc/', include('mozilla_django_oidc.urls')),
        path("login/failed/", RedirectView.as_view(pattern_name="oidc_authentication_init"), name="login"),
        path("logout/", RedirectView.as_view(pattern_name="oidc_logout"), name="logout"),
        path("login/", RedirectView.as_view(pattern_name="oidc_authentication_init"), name="login"),
        path("i18n/", include("django.conf.urls.i18n")),
        path("admin/", admin.site.urls),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

handler401 = "django.views.defaults.page_not_found"
handler403 = "django.views.defaults.page_not_found"
handler404 = "django.views.defaults.page_not_found"
