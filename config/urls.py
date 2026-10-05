"""Rotas principais do projeto."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

admin.site.site_header = "Protetor RF2 · Administração"
admin.site.site_title = "Protetor RF2"
admin.site.index_title = "Gestão do projeto"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "entrar/",
        auth_views.LoginView.as_view(redirect_authenticated_user=True),
        name="login",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("", include("animais.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
