"""
Popula o banco com dados FICTÍCIOS para demonstração.

Uso:
    python manage.py popular_dados          # cria se o banco estiver vazio
    python manage.py popular_dados --publico # demonstração pública sem contas de login
    python manage.py popular_dados --limpar # apaga cães/protetores e recria
"""
from datetime import timedelta
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from animais.models import Cao, ConfiguracaoSite, HistoricoStatus, Protetor

PASTA_IMAGENS = Path(settings.BASE_DIR) / "seed" / "imagens"
SENHA_PADRAO = "protetor123"

PROTETORES = [
    ("ana", "Ana", "Ribeiro", "(61) 99811-2233", "Asa Norte"),
    ("bruno", "Bruno", "Lima", "(61) 99722-3344", "Taguatinga"),
    ("carla", "Carla", "Souza", "(61) 99633-4455", "Guará"),
]

# (nome, sexo, porte, faixa, idade, local, protetor, status, castrado, vacinado,
#  vermifugado, imagem, descricao, comportamento, saude, historico)
CAES = [
    ("Paçoca", "M", "M", "adulto", "cerca de 2 anos", "Asa Norte – Brasília", "ana", "disponivel",
     True, True, True, "caramelo",
     "Paçoca foi resgatado perto de uma parada de ônibus e hoje é o mascote do lar temporário. "
     "Caramelo legítimo: leal, brincalhão e apaixonado por passeios.",
     "Convive bem com outros cães e crianças. Aprendeu a sentar e dar a pata.",
     "Saudável, castrado e com vacinas em dia.",
     ["tratamento", "lar_temporario", "disponivel"]),
    ("Feijão", "M", "P", "filhote", "3 meses", "Taguatinga", "bruno", "lar_temporario",
     False, True, True, "filhote",
     "Feijão foi encontrado com os irmãos em uma caixa. Está crescendo forte e cheio de energia.",
     "Curioso e carinhoso. Está aprendendo a fazer as necessidades no tapete higiênico.",
     "Primeira dose da vacina V10 aplicada. Castração prevista para os 6 meses.",
     ["tratamento", "lar_temporario"]),
    ("Seu Jorge", "M", "G", "idoso", "cerca de 9 anos", "Guará", "carla", "disponivel",
     True, True, True, "idoso",
     "Seu Jorge viveu anos em uma obra até ser resgatado. Calmo e muito educado, procura um lar "
     "tranquilo para aproveitar a melhor idade.",
     "Tranquilo, anda bem na guia e adora um cafuné. Ideal para apartamento.",
     "Faz acompanhamento de artrose leve com suplemento.",
     ["tratamento", "disponivel"]),
    ("Tigresa", "F", "M", "adulto", "1 ano", "Sobradinho", "ana", "em_adocao",
     True, True, True, "tigrado",
     "Tigresa é pura energia! Ótima companheira para quem gosta de correr e fazer trilhas.",
     "Muito ativa e inteligente. Precisa de casa com quintal e passeios diários.",
     "Castrada e vacinada.",
     ["tratamento", "disponivel", "em_adocao"]),
    ("Radar", "M", "M", "adulto", "cerca de 3 anos", "Ceilândia", "carla", "tratamento",
     False, False, True, "orelha",
     "Radar ganhou esse nome por causa das orelhas. Está se recuperando de uma lesão na pata.",
     "Dócil com pessoas; ainda em avaliação com outros cães.",
     "Em tratamento de lesão na pata traseira. Retorno ao veterinário em duas semanas.",
     ["tratamento"]),
    ("Mel", "F", "P", "adulto", "4 anos", "Águas Claras", "bruno", "adotado",
     True, True, True, "branca",
     "Mel foi adotada por uma família de Águas Claras e hoje é a rainha do sofá.",
     "Companheira e tranquila.", "Saudável.",
     ["tratamento", "disponivel", "em_adocao", "adotado"]),
    ("Pretinha", "F", "M", "adulto", "2 anos", "Vicente Pires", "ana", "adotado",
     True, True, True, "adotado_sofa",
     "Pretinha encontrou um lar cheio de amor após três meses em lar temporário.",
     "Brincalhona.", "Saudável.",
     ["tratamento", "lar_temporario", "disponivel", "adotado"]),
    ("Amendoim", "M", "G", "adulto", "3 anos", "Gama", "carla", "adotado",
     True, True, True, "adotado_praia",
     "Amendoim agora tem um jardim só dele e um irmão humano de 7 anos.",
     "Sociável.", "Saudável.",
     ["disponivel", "em_adocao", "adotado"]),
]

OBSERVACOES = {
    "tratamento": "Resgate realizado e primeira consulta veterinária.",
    "lar_temporario": "Encaminhado para lar temporário.",
    "disponivel": "Liberado pelo veterinário para adoção.",
    "em_adocao": "Entrevista realizada; visita agendada.",
    "adotado": "Termo de adoção assinado. Acompanhamento por 6 meses.",
}


class Command(BaseCommand):
    help = "Cria protetores, cães e configuração de exemplo (dados fictícios)."

    def add_arguments(self, parser):
        parser.add_argument("--limpar", action="store_true", help="Remove os dados existentes antes.")
        parser.add_argument(
            "--publico",
            action="store_true",
            help="Não cria outro administrador e desativa as contas fictícias de protetores.",
        )

    @transaction.atomic
    def handle(self, *args, limpar=False, publico=False, **opts):
        User = get_user_model()
        if limpar and publico:
            raise CommandError("Não combine --limpar com --publico.")

        if limpar:
            Cao.objects.all().delete()
            Protetor.objects.all().delete()
            User.objects.filter(username__in=[p[0] for p in PROTETORES]).delete()
        elif Cao.objects.exists():
            self.stdout.write(self.style.WARNING("Já existem cães cadastrados. Use --limpar para recriar."))
            return

        if publico:
            conflitos = list(
                User.objects.filter(username__in=[p[0] for p in PROTETORES])
                .values_list("username", flat=True)
            )
            if conflitos:
                nomes = ", ".join(conflitos)
                raise CommandError(
                    f"Já existem contas com os nomes reservados para a demonstração: {nomes}. "
                    "Renomeie-as antes de popular para não alterar contas existentes."
                )

        config = ConfiguracaoSite.obter()
        config.nome_projeto = "Patas de Brasília"
        config.slogan = "Adoção responsável que transforma vidas."
        config.chave_pix = "doacoes@patasdebrasilia.org"
        config.favorecido_pix = "Associação Patas de Brasília (exemplo)"
        config.instagram = "@patasdebrasilia"
        config.email = "contato@patasdebrasilia.org"
        config.save()

        protetores = {}
        for username, nome, sobrenome, whats, regiao in PROTETORES:
            user, _ = User.objects.get_or_create(
                username=username, defaults={"first_name": nome, "last_name": sobrenome}
            )
            if publico:
                user.set_unusable_password()
                user.is_active = False
            else:
                user.set_password(SENHA_PADRAO)
            user.save()
            protetores[username], _ = Protetor.objects.get_or_create(
                usuario=user, defaults={"whatsapp": whats, "regiao": regiao}
            )

        if not publico and not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123", first_name="Admin")

        agora = timezone.now()
        for i, (nome, sexo, porte, faixa, idade, local, prot, status, cast, vac, verm, img,
                desc, comp, saude, hist) in enumerate(CAES):
            cao = Cao(
                nome=nome, sexo=sexo, porte=porte, faixa_etaria=faixa, idade_aproximada=idade,
                localizacao=local, protetor=protetores[prot], status=status, castrado=cast,
                vacinado=vac, vermifugado=verm, descricao=desc, comportamento=comp, saude=saude,
            )
            if status == "adotado":
                cao.data_adocao = (agora - timedelta(days=20 + i * 25)).date()
            with open(PASTA_IMAGENS / f"{img}.jpg", "rb") as f:
                cao.foto.save(f"{img}.jpg", File(f), save=False)
            cao.save()

            anterior = ""
            total = len(hist)
            for passo, st in enumerate(hist):
                h = HistoricoStatus.objects.create(
                    cao=cao, status_anterior=anterior, status_novo=st,
                    observacao=OBSERVACOES[st], autor=protetores[prot].usuario,
                )
                # Distribui as datas no passado para um histórico realista
                HistoricoStatus.objects.filter(pk=h.pk).update(
                    criado_em=agora - timedelta(days=(total - passo) * 9 + i, hours=passo)
                )
                anterior = st

        mensagem = f"Dados criados: {len(PROTETORES)} protetores e {len(CAES)} cães."
        if publico:
            mensagem += " Contas fictícias desativadas; nenhum administrador novo foi criado."
        else:
            mensagem += f"\nLogin de protetor: ana / {SENHA_PADRAO}  ·  Admin: admin / admin123"
        self.stdout.write(self.style.SUCCESS(mensagem))
