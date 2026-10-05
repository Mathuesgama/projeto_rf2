"""Testes automatizados das principais regras do MVP."""
import shutil
import tempfile
from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Cao, HistoricoStatus, Protetor

# GIF 1x1 válido para os uploads de teste
GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,"
    b"\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)
MEDIA_TMP = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_TMP)
class BaseTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TMP, ignore_errors=True)

    def setUp(self):
        self.user = get_user_model().objects.create_user("ana", password="senha-forte-123", first_name="Ana")
        self.protetor = Protetor.objects.create(usuario=self.user, whatsapp="(61) 99999-0000")

    def criar_cao(self, **kw):
        dados = dict(
            nome="Paçoca", sexo="M", idade_aproximada="2 anos", localizacao="Asa Norte",
            protetor=self.protetor, status=Cao.Status.DISPONIVEL,
            foto=SimpleUploadedFile("f.gif", GIF, content_type="image/gif"),
        )
        dados.update(kw)
        return Cao.objects.create(**dados)


class AreaPublicaTest(BaseTest):
    def test_vitrine_exibe_apenas_status_publicos(self):
        self.criar_cao(nome="Visivel")
        self.criar_cao(nome="Oculto", status=Cao.Status.TRATAMENTO)
        resp = self.client.get(reverse("animais:lista"))
        self.assertContains(resp, "Visivel")
        self.assertNotContains(resp, "Oculto")

    def test_detalhe_em_tratamento_retorna_404_para_anonimo(self):
        cao = self.criar_cao(status=Cao.Status.TRATAMENTO)
        self.assertEqual(self.client.get(cao.get_absolute_url()).status_code, 404)

    def test_link_whatsapp_usa_numero_do_protetor(self):
        cao = self.criar_cao()
        resp = self.client.get(cao.get_absolute_url())
        self.assertContains(resp, "https://wa.me/5561999990000?text=")

    def test_filtro_por_sexo(self):
        self.criar_cao(nome="Rex", sexo="M")
        self.criar_cao(nome="Luna", sexo="F")
        resp = self.client.get(reverse("animais:lista"), {"sexo": "F"})
        self.assertContains(resp, "Luna")
        self.assertNotContains(resp, "Rex")


class AreaInternaTest(BaseTest):
    def test_painel_exige_login(self):
        resp = self.client.get(reverse("animais:painel"))
        self.assertRedirects(resp, f"{reverse('login')}?next={reverse('animais:painel')}")

    def test_cadastro_cria_historico_inicial(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("animais:novo"), {
            "nome": "Feijão", "sexo": "M", "porte": "P", "faixa_etaria": "filhote",
            "idade_aproximada": "3 meses", "localizacao": "Taguatinga",
            "protetor": self.protetor.pk, "status": "tratamento",
            "foto": SimpleUploadedFile("f.gif", GIF, content_type="image/gif"),
        })
        cao = Cao.objects.get(nome="Feijão")
        self.assertRedirects(resp, reverse("animais:gerenciar", args=[cao.pk]))
        self.assertEqual(cao.historico.count(), 1)

    def test_atualizar_status_registra_historico(self):
        cao = self.criar_cao()
        self.client.force_login(self.user)
        self.client.post(reverse("animais:status", args=[cao.pk]), {
            "status": "adotado", "data_adocao": "2026-10-01", "observacao": "Termo assinado",
        })
        cao.refresh_from_db()
        self.assertEqual(cao.status, Cao.Status.ADOTADO)
        self.assertEqual(cao.data_adocao, date(2026, 10, 1))
        h = HistoricoStatus.objects.get(cao=cao)
        self.assertEqual((h.status_anterior, h.status_novo), ("disponivel", "adotado"))

    def test_adotado_exige_data(self):
        cao = self.criar_cao()
        self.client.force_login(self.user)
        resp = self.client.post(reverse("animais:status", args=[cao.pk]), {"status": "adotado"})
        self.assertEqual(resp.status_code, 200)
        cao.refresh_from_db()
        self.assertEqual(cao.status, Cao.Status.DISPONIVEL)

    def test_filtro_meus_caes(self):
        outro_user = get_user_model().objects.create_user("bruno", password="x")
        outro = Protetor.objects.create(usuario=outro_user, whatsapp="61988887777")
        self.criar_cao(nome="DaAna")
        self.criar_cao(nome="DoBruno", protetor=outro)
        self.client.force_login(self.user)
        resp = self.client.get(reverse("animais:painel"), {"protetor": "meus"})
        self.assertContains(resp, "DaAna")
        self.assertNotContains(resp, "DoBruno")
