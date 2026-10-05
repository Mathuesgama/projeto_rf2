from .models import ConfiguracaoSite


def configuracao_site(request):
    """Disponibiliza os dados do projeto (nome, PIX, redes) em todos os templates."""
    return {"site": ConfiguracaoSite.obter()}
