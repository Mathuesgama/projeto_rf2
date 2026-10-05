from django import forms

from .models import Cao, Protetor


class MultiplasImagensInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiplasImagensField(forms.ImageField):
    """Campo que aceita várias imagens em um único input (RF02)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultiplasImagensInput(attrs={"accept": "image/*"}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        limpar = super().clean
        if isinstance(data, (list, tuple)):
            return [limpar(d, initial) for d in data if d]
        return [limpar(data, initial)] if data else []


class CaoForm(forms.ModelForm):
    fotos_extras = MultiplasImagensField(
        label="Fotos adicionais",
        required=False,
        help_text="Opcional. Selecione uma ou mais imagens.",
    )
    observacao_status = forms.CharField(
        label="Observação sobre a situação",
        required=False,
        max_length=255,
        help_text="Registrada no histórico quando a situação for alterada.",
    )

    class Meta:
        model = Cao
        fields = [
            "nome", "sexo", "porte", "faixa_etaria", "idade_aproximada", "localizacao",
            "protetor", "status", "data_adocao", "castrado", "vacinado", "vermifugado",
            "saude", "comportamento", "descricao", "observacoes_internas", "foto",
        ]
        widgets = {
            "data_adocao": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "foto": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "saude": forms.Textarea(attrs={"rows": 3}),
            "comportamento": forms.Textarea(attrs={"rows": 3}),
            "descricao": forms.Textarea(attrs={"rows": 4}),
            "observacoes_internas": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["protetor"].queryset = Protetor.objects.select_related("usuario")
        # Sugere o protetor logado como responsável em novos cadastros
        if not self.instance.pk and usuario is not None and hasattr(usuario, "protetor"):
            self.fields["protetor"].initial = usuario.protetor

    def clean(self):
        dados = super().clean()
        if dados.get("status") == Cao.Status.ADOTADO and not dados.get("data_adocao"):
            self.add_error("data_adocao", "Informe a data da adoção para cães adotados.")
        return dados


class StatusForm(forms.Form):
    """Atualização rápida da situação a partir do painel (RNF02)."""

    status = forms.ChoiceField(label="Nova situação", choices=Cao.Status.choices)
    observacao = forms.CharField(
        label="Observação",
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "Ex.: entrevista realizada, visita agendada…"}),
    )
    data_adocao = forms.DateField(
        label="Data da adoção", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )

    def clean(self):
        dados = super().clean()
        if dados.get("status") == Cao.Status.ADOTADO and not dados.get("data_adocao"):
            self.add_error("data_adocao", "Informe a data da adoção.")
        return dados


class FiltroCaesForm(forms.Form):
    """Filtros da vitrine pública."""

    q = forms.CharField(label="Buscar", required=False,
                        widget=forms.SearchInput(attrs={"placeholder": "Nome ou região"}))
    sexo = forms.ChoiceField(label="Sexo", required=False,
                             choices=[("", "Todos")] + list(Cao.Sexo.choices))
    porte = forms.ChoiceField(label="Porte", required=False,
                              choices=[("", "Todos")] + list(Cao.Porte.choices))
    faixa_etaria = forms.ChoiceField(label="Idade", required=False,
                                     choices=[("", "Todas")] + list(Cao.FaixaEtaria.choices))
