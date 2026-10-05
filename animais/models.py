"""
Modelos de domínio.

Mapeamento com os requisitos definidos no Módulo 1:
- Protetor ............ RF01 / RF05 (responsável pelos animais)
- Cao ................. RF02 / RF03 / RF04
- FotoCao ............. RF02 (fotografias adicionais)
- HistoricoStatus ..... RF03 / RF08 (andamento e histórico)
- ConfiguracaoSite .... RF06 / RF07 (contato geral e chave PIX)
"""
import re
from urllib.parse import quote

from django.conf import settings
from django.db import models
from django.urls import reverse


def apenas_digitos(valor: str) -> str:
    return re.sub(r"\D", "", valor or "")


class Protetor(models.Model):
    """Perfil do protetor vinculado a um usuário do Django (autenticação)."""

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="protetor"
    )
    whatsapp = models.CharField(
        "WhatsApp",
        max_length=20,
        help_text="Com DDD. Ex.: (61) 99999-0000. Usado no botão de contato para adoção.",
    )
    regiao = models.CharField("Região de atuação", max_length=80, blank=True)

    class Meta:
        verbose_name = "protetor"
        verbose_name_plural = "protetores"
        ordering = ["usuario__first_name", "usuario__username"]

    def __str__(self):
        return self.usuario.get_full_name() or self.usuario.username

    @property
    def whatsapp_internacional(self) -> str:
        digitos = apenas_digitos(self.whatsapp)
        return digitos if digitos.startswith("55") else f"55{digitos}"


class Cao(models.Model):
    class Sexo(models.TextChoices):
        MACHO = "M", "Macho"
        FEMEA = "F", "Fêmea"

    class Porte(models.TextChoices):
        PEQUENO = "P", "Pequeno"
        MEDIO = "M", "Médio"
        GRANDE = "G", "Grande"

    class FaixaEtaria(models.TextChoices):
        FILHOTE = "filhote", "Filhote"
        ADULTO = "adulto", "Adulto"
        IDOSO = "idoso", "Idoso"

    class Status(models.TextChoices):
        TRATAMENTO = "tratamento", "Em tratamento"
        LAR_TEMPORARIO = "lar_temporario", "Em lar temporário"
        DISPONIVEL = "disponivel", "Disponível para adoção"
        EM_ADOCAO = "em_adocao", "Em processo de adoção"
        ADOTADO = "adotado", "Adotado"

    # Status exibidos na vitrine pública (RF04)
    STATUS_PUBLICOS = (Status.LAR_TEMPORARIO, Status.DISPONIVEL, Status.EM_ADOCAO)

    nome = models.CharField(max_length=60)
    sexo = models.CharField(max_length=1, choices=Sexo.choices)
    porte = models.CharField(max_length=1, choices=Porte.choices, default=Porte.MEDIO)
    faixa_etaria = models.CharField(
        "faixa etária", max_length=10, choices=FaixaEtaria.choices, default=FaixaEtaria.ADULTO
    )
    idade_aproximada = models.CharField(
        "idade aproximada", max_length=40, help_text="Ex.: 3 meses, 2 anos, cerca de 8 anos."
    )
    localizacao = models.CharField(
        "localização", max_length=100, help_text="Região onde o animal está (sem endereço completo)."
    )
    protetor = models.ForeignKey(
        Protetor, on_delete=models.PROTECT, related_name="caes", verbose_name="protetor responsável"
    )
    castrado = models.BooleanField(default=False)
    vacinado = models.BooleanField(default=False)
    vermifugado = models.BooleanField(default=False)
    saude = models.TextField("condições de saúde", blank=True)
    comportamento = models.TextField(blank=True)
    descricao = models.TextField(
        "sobre o animal", blank=True, help_text="Texto público exibido na página de divulgação."
    )
    observacoes_internas = models.TextField(
        "observações internas", blank=True, help_text="Visível apenas para protetores autenticados."
    )
    foto = models.ImageField("foto principal", upload_to="caes/")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRATAMENTO)
    data_adocao = models.DateField("data da adoção", null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "cão"
        verbose_name_plural = "cães"
        ordering = ["-atualizado_em"]

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        return reverse("animais:detalhe", args=[self.pk])

    @property
    def publico(self) -> bool:
        return self.status in self.STATUS_PUBLICOS or self.status == self.Status.ADOTADO

    @property
    def artigo(self) -> str:
        return "a" if self.sexo == self.Sexo.FEMEA else "o"

    def link_whatsapp(self, url_pagina: str = "") -> str:
        """Link wa.me com mensagem pronta para o protetor responsável (RF06)."""
        texto = (
            f"Olá! Vi {self.artigo} {self.nome} no site de adoção e tenho interesse "
            f"em saber mais sobre a adoção responsável."
        )
        if url_pagina:
            texto += f" {url_pagina}"
        return f"https://wa.me/{self.protetor.whatsapp_internacional}?text={quote(texto)}"


class FotoCao(models.Model):
    cao = models.ForeignKey(Cao, on_delete=models.CASCADE, related_name="fotos")
    imagem = models.ImageField(upload_to="caes/extras/")
    enviada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "foto adicional"
        verbose_name_plural = "fotos adicionais"
        ordering = ["enviada_em"]

    def __str__(self):
        return f"Foto de {self.cao}"


class HistoricoStatus(models.Model):
    """Registro de cada mudança de situação do animal (RF03 / RF08)."""

    cao = models.ForeignKey(Cao, on_delete=models.CASCADE, related_name="historico")
    status_anterior = models.CharField(max_length=20, choices=Cao.Status.choices, blank=True)
    status_novo = models.CharField(max_length=20, choices=Cao.Status.choices)
    observacao = models.CharField("observação", max_length=255, blank=True)
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "histórico de status"
        verbose_name_plural = "históricos de status"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.cao}: {self.get_status_novo_display()}"


class ConfiguracaoSite(models.Model):
    """Configuração única editável pelo admin (dados do projeto e doação)."""

    nome_projeto = models.CharField(max_length=80, default="Patas de Brasília")
    slogan = models.CharField(max_length=160, default="Adoção responsável que transforma vidas.")
    sobre = models.TextField(
        blank=True,
        default="Somos um grupo de protetores independentes que resgata, trata e "
        "encaminha cães para lares responsáveis.",
    )
    chave_pix = models.CharField("chave PIX", max_length=120, blank=True)
    favorecido_pix = models.CharField("favorecido do PIX", max_length=120, blank=True)
    instagram = models.CharField("Instagram (@)", max_length=60, blank=True)
    whatsapp_geral = models.CharField("WhatsApp geral", max_length=20, blank=True)
    email = models.EmailField("e-mail", blank=True)

    class Meta:
        verbose_name = "configuração do site"
        verbose_name_plural = "configuração do site"

    def __str__(self):
        return self.nome_projeto

    def save(self, *args, **kwargs):
        self.pk = 1  # garante registro único
        super().save(*args, **kwargs)

    @classmethod
    def obter(cls) -> "ConfiguracaoSite":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def instagram_url(self) -> str:
        return f"https://instagram.com/{self.instagram.lstrip('@')}" if self.instagram else ""
