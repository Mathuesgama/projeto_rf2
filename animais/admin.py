from django.contrib import admin
from django.utils.html import format_html

from .models import Cao, ConfiguracaoSite, FotoCao, HistoricoStatus, Protetor


@admin.register(Protetor)
class ProtetorAdmin(admin.ModelAdmin):
    list_display = ("__str__", "whatsapp", "regiao")
    search_fields = ("usuario__first_name", "usuario__last_name", "usuario__username")


class FotoCaoInline(admin.TabularInline):
    model = FotoCao
    extra = 0


class HistoricoInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0
    readonly_fields = ("status_anterior", "status_novo", "observacao", "autor", "criado_em")
    can_delete = False


@admin.register(Cao)
class CaoAdmin(admin.ModelAdmin):
    list_display = ("miniatura", "nome", "status", "protetor", "sexo", "porte", "atualizado_em")
    list_display_links = ("miniatura", "nome")
    list_filter = ("status", "protetor", "sexo", "porte", "faixa_etaria", "castrado")
    search_fields = ("nome", "localizacao")
    inlines = [FotoCaoInline, HistoricoInline]

    @admin.display(description="Foto")
    def miniatura(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" alt="" style="width:48px;height:48px;object-fit:cover;border-radius:8px">',
                obj.foto.url,
            )
        return "—"


@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ("cao", "status_anterior", "status_novo", "autor", "criado_em")
    list_filter = ("status_novo",)


@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ConfiguracaoSite.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
