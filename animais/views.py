"""
Views da aplicação.

Área pública (sem login): início, vitrine, detalhe, adotados e apoio.
Área interna (login obrigatório — RNF03): painel, cadastro, edição, status e exclusão.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView,
)

from .forms import CaoForm, FiltroCaesForm, StatusForm
from .models import Cao, FotoCao, HistoricoStatus, Protetor


# --------------------------------------------------------------------------- #
# Área pública
# --------------------------------------------------------------------------- #
class InicioView(TemplateView):
    template_name = "animais/inicio.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        publicos = Cao.objects.filter(status__in=Cao.STATUS_PUBLICOS)
        ctx["destaques"] = publicos.select_related("protetor__usuario")[:6]
        ctx["total_disponiveis"] = publicos.count()
        ctx["total_adotados"] = Cao.objects.filter(status=Cao.Status.ADOTADO).count()
        ctx["total_protetores"] = Protetor.objects.count()
        return ctx


class CaoListView(ListView):
    """Vitrine pública com filtros (RF04)."""

    template_name = "animais/lista.html"
    context_object_name = "caes"
    paginate_by = 9

    def get_queryset(self):
        qs = Cao.objects.filter(status__in=Cao.STATUS_PUBLICOS).select_related("protetor__usuario")
        self.filtro = FiltroCaesForm(self.request.GET or None)
        if self.filtro.is_valid():
            d = self.filtro.cleaned_data
            if d.get("q"):
                qs = qs.filter(Q(nome__icontains=d["q"]) | Q(localizacao__icontains=d["q"]))
            for campo in ("sexo", "porte", "faixa_etaria"):
                if d.get(campo):
                    qs = qs.filter(**{campo: d[campo]})
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filtro"] = self.filtro
        return ctx


class CaoDetailView(DetailView):
    template_name = "animais/detalhe.html"
    context_object_name = "cao"

    def get_queryset(self):
        return Cao.objects.select_related("protetor__usuario").prefetch_related("fotos")

    def get_object(self, queryset=None):
        cao = super().get_object(queryset)
        # Animais em tratamento só são visíveis para protetores autenticados
        if not cao.publico and not self.request.user.is_authenticated:
            raise Http404
        return cao

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        url = self.request.build_absolute_uri(self.object.get_absolute_url())
        ctx["url_pagina"] = url
        ctx["link_whatsapp"] = self.object.link_whatsapp(url)
        ctx["outros"] = (
            Cao.objects.filter(status__in=Cao.STATUS_PUBLICOS)
            .exclude(pk=self.object.pk)
            .select_related("protetor__usuario")[:3]
        )
        return ctx


class AdotadosView(ListView):
    """Histórico público de animais adotados (RF08)."""

    template_name = "animais/adotados.html"
    context_object_name = "caes"
    paginate_by = 12

    def get_queryset(self):
        return Cao.objects.filter(status=Cao.Status.ADOTADO).order_by("-data_adocao", "-atualizado_em")


class ApoieView(TemplateView):
    """Seção de apoio com chave PIX (RF07)."""

    template_name = "animais/apoie.html"


# --------------------------------------------------------------------------- #
# Área interna
# --------------------------------------------------------------------------- #
def registrar_status(cao, anterior, usuario, observacao=""):
    HistoricoStatus.objects.create(
        cao=cao,
        status_anterior=anterior or "",
        status_novo=cao.status,
        observacao=observacao,
        autor=usuario,
    )


class PainelView(LoginRequiredMixin, ListView):
    """Painel com indicadores e filtro por protetor responsável (RF05)."""

    template_name = "animais/painel.html"
    context_object_name = "caes"
    paginate_by = 20

    def get_queryset(self):
        qs = Cao.objects.select_related("protetor__usuario")
        self.protetor_sel = self.request.GET.get("protetor", "")
        self.status_sel = self.request.GET.get("status", "")
        if self.protetor_sel == "meus" and hasattr(self.request.user, "protetor"):
            qs = qs.filter(protetor=self.request.user.protetor)
        elif self.protetor_sel.isdigit():
            qs = qs.filter(protetor_id=int(self.protetor_sel))
        if self.status_sel in Cao.Status.values:
            qs = qs.filter(status=self.status_sel)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        contagem = dict(Cao.objects.values_list("status").annotate(n=Count("id")))
        ctx["indicadores"] = [
            {"valor": v, "rotulo": r, "total": contagem.get(v, 0)} for v, r in Cao.Status.choices
        ]
        ctx["protetores"] = Protetor.objects.select_related("usuario").annotate(
            total=Count("caes", filter=~Q(caes__status=Cao.Status.ADOTADO))
        )
        ctx["protetor_sel"] = self.protetor_sel
        ctx["status_sel"] = self.status_sel
        ctx["status_choices"] = Cao.Status.choices
        ctx["recentes"] = HistoricoStatus.objects.select_related("cao", "autor")[:6]
        return ctx


class CaoFormMixin(LoginRequiredMixin):
    model = Cao
    form_class = CaoForm
    template_name = "animais/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["usuario"] = self.request.user
        return kwargs

    def salvar_fotos(self, form):
        for imagem in form.cleaned_data.get("fotos_extras", []):
            FotoCao.objects.create(cao=self.object, imagem=imagem)

    def get_success_url(self):
        return reverse("animais:gerenciar", args=[self.object.pk])


class CaoCreateView(CaoFormMixin, CreateView):
    def form_valid(self, form):
        resposta = super().form_valid(form)
        self.salvar_fotos(form)
        registrar_status(self.object, "", self.request.user,
                         form.cleaned_data.get("observacao_status") or "Cadastro inicial")
        messages.success(self.request, f"{self.object.nome} foi cadastrad{self.object.artigo} com sucesso!")
        return resposta


class CaoUpdateView(CaoFormMixin, UpdateView):
    def form_valid(self, form):
        anterior = Cao.objects.only("status").get(pk=self.object.pk).status
        resposta = super().form_valid(form)
        self.salvar_fotos(form)
        if anterior != self.object.status:
            registrar_status(self.object, anterior, self.request.user,
                             form.cleaned_data.get("observacao_status", ""))
        messages.success(self.request, "Cadastro atualizado.")
        return resposta


class CaoGerenciarView(LoginRequiredMixin, DetailView):
    """Ficha interna do animal com histórico e atualização rápida de status."""

    template_name = "animais/gerenciar.html"
    context_object_name = "cao"

    def get_queryset(self):
        return Cao.objects.select_related("protetor__usuario").prefetch_related(
            "fotos", "historico__autor"
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["status_form"] = kwargs.get("status_form") or StatusForm(
            initial={"status": self.object.status, "data_adocao": self.object.data_adocao}
        )
        return ctx


class AtualizarStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        cao = get_object_or_404(Cao, pk=pk)
        form = StatusForm(request.POST)
        if not form.is_valid():
            view = CaoGerenciarView()
            view.setup(request, pk=pk)
            view.object = cao
            return view.render_to_response(view.get_context_data(status_form=form))
        anterior = cao.status
        cao.status = form.cleaned_data["status"]
        if cao.status == Cao.Status.ADOTADO:
            cao.data_adocao = form.cleaned_data["data_adocao"]
        cao.save()
        registrar_status(cao, anterior, request.user, form.cleaned_data["observacao"])
        messages.success(request, f"Situação atualizada para “{cao.get_status_display()}”.")
        return redirect("animais:gerenciar", pk=cao.pk)


class CaoDeleteView(LoginRequiredMixin, DeleteView):
    model = Cao
    template_name = "animais/confirmar_exclusao.html"
    context_object_name = "cao"
    success_url = reverse_lazy("animais:painel")

    def form_valid(self, form):
        messages.success(self.request, f"{self.object.nome} foi removid{self.object.artigo} do sistema.")
        return super().form_valid(form)


class FotoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        foto = get_object_or_404(FotoCao, pk=pk)
        cao_pk = foto.cao_id
        foto.imagem.delete(save=False)
        foto.delete()
        messages.success(request, "Foto removida.")
        return redirect("animais:gerenciar", pk=cao_pk)
