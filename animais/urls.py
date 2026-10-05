from django.urls import path

from . import views

app_name = "animais"

urlpatterns = [
    # Público
    path("", views.InicioView.as_view(), name="inicio"),
    path("caes/", views.CaoListView.as_view(), name="lista"),
    path("caes/<int:pk>/", views.CaoDetailView.as_view(), name="detalhe"),
    path("adotados/", views.AdotadosView.as_view(), name="adotados"),
    path("apoie/", views.ApoieView.as_view(), name="apoie"),
    # Interno (protetores autenticados)
    path("painel/", views.PainelView.as_view(), name="painel"),
    path("painel/caes/novo/", views.CaoCreateView.as_view(), name="novo"),
    path("painel/caes/<int:pk>/", views.CaoGerenciarView.as_view(), name="gerenciar"),
    path("painel/caes/<int:pk>/editar/", views.CaoUpdateView.as_view(), name="editar"),
    path("painel/caes/<int:pk>/status/", views.AtualizarStatusView.as_view(), name="status"),
    path("painel/caes/<int:pk>/excluir/", views.CaoDeleteView.as_view(), name="excluir"),
    path("painel/fotos/<int:pk>/excluir/", views.FotoDeleteView.as_view(), name="excluir_foto"),
]
