# 🐾 Patas de Brasília — Plataforma de Adoção Responsável de Cães

Aplicação web desenvolvida em **Django** para apoiar protetores independentes na **organização, divulgação e acompanhamento** de cães resgatados e disponíveis para adoção.

> Projeto Integrador de Tecnologia da Informação II — Programa de Extensão UFMS Digital
> Autor: **Matheus Leal da Gama**

O problema foi levantado no Módulo 1 por meio de entrevista com protetores: as informações dos animais ficavam espalhadas entre WhatsApp, Instagram, planilhas, cadernos e documentos, dificultando saber quem é responsável por cada cão e qual a sua situação atual. Esta aplicação centraliza esses dados e oferece uma vitrine pública sempre atualizada.

---

## ✨ Funcionalidades (MVP)

| Requisito | Funcionalidade |
|---|---|
| **RF01** | Login de protetores (autenticação do Django) |
| **RF02** | Cadastro de cães com nome, localização, responsável, idade, sexo, porte, castração, vacinas, saúde, comportamento, observações e fotos (principal + adicionais) |
| **RF03** | Atualização da situação: *em tratamento*, *em lar temporário*, *disponível*, *em processo de adoção* e *adotado* |
| **RF04** | Vitrine pública com filtros (sexo, porte, idade, busca) e página individual pronta para compartilhar |
| **RF05** | Painel com filtro por protetor responsável e opção “Somente os meus” |
| **RF06** | Botão “Quero adotar” que abre o WhatsApp do protetor com mensagem pronta |
| **RF07** | Página “Apoie” com chave PIX configurável e botão de copiar |
| **RF08** | Histórico de mudanças de status (quem, quando e observação) e página pública “Finais felizes” |
| **RNF01** | Layout responsivo *mobile-first* (breakpoints 640 px e 960 px) |
| **RNF02** | Atualização de status em um único formulário curto |
| **RNF03** | Área interna protegida por login (`LoginRequiredMixin`) |
| **RNF04** | Coleta mínima de dados; observações internas e cães em tratamento não são públicos |

## 🛠️ Tecnologias

- **Python 3.12+** e **Django 5.2** (MVT, ORM, autenticação, admin, formulários)
- **HTML5 semântico** (landmarks, `aria-*`, skip link, hierarquia de títulos)
- **CSS3 puro** (custom properties, Grid, Flexbox, `clamp()`, media queries)
- **JavaScript** apenas como melhoria progressiva (menu, galeria, copiar PIX, Web Share API)
- **SQLite** em desenvolvimento (substituível por PostgreSQL)
- **Pillow** para upload de imagens

## 📁 Estrutura

```
protetor_rf2/
├── config/                 # Configurações do projeto (settings, urls, wsgi)
├── animais/                # App principal
│   ├── models.py           # Protetor, Cao, FotoCao, HistoricoStatus, ConfiguracaoSite
│   ├── views.py            # Views públicas e internas (CBVs)
│   ├── forms.py            # Formulários com validação
│   ├── admin.py            # Painel administrativo
│   ├── tests.py            # Testes automatizados
│   └── management/commands/popular_dados.py  # Dados de exemplo
├── templates/              # Templates HTML (base, partials, páginas)
├── static/                 # CSS, JS e imagens
├── seed/imagens/           # Fotos usadas nos dados de exemplo
├── manage.py
└── requirements.txt
```

## 🚀 Instalação e execução

```bash
# 1. Clonar o repositório
git clone <URL-DO-REPOSITORIO>
cd protetor_rf2

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar o banco e popular com dados de exemplo (fictícios)
python manage.py migrate
python manage.py popular_dados

# Em uma demonstração pública, substitua a linha anterior por esta opção:
# python manage.py popular_dados --publico

# 5. Executar
python manage.py runserver
```

Acesse **http://127.0.0.1:8000/**.

### Usuários de demonstração

O comando local `popular_dados` cria contas de demonstração com as credenciais abaixo. Não use essas contas em um site público. Para publicar dados fictícios sem criar outro administrador nem permitir login com as contas dos protetores, execute `python manage.py popular_dados --publico`.

| Perfil | Usuário | Senha |
|---|---|---|
| Protetor | `ana` / `bruno` / `carla` | `protetor123` |
| Administrador (`/admin/`) | `admin` | `admin123` |

> ⚠️ Os dados, telefones e chave PIX são **fictícios**. Altere-os pelo `/admin/` (Configuração do site e Protetores) antes de usar em produção.

## 🧭 Como usar

1. **Visitante:** navegue em *Adote*, filtre os cães, abra um perfil e clique em **Quero adotar** para falar com o protetor pelo WhatsApp, ou em **Compartilhar perfil**.
2. **Protetor:** entre em *Área do protetor* → **Painel**. Veja os indicadores por situação, filtre por responsável, cadastre um novo cão ou abra a ficha de um animal para **registrar a atualização de situação** (o histórico é gravado automaticamente).
3. **Administrador:** em `/admin/` cadastre novos protetores (usuário + perfil com WhatsApp) e edite nome do projeto, redes sociais e chave PIX.

## ✅ Testes

```bash
python manage.py test animais
```

Os testes cobrem: visibilidade pública por status, 404 para cães em tratamento, link do WhatsApp, filtros, exigência de login, histórico no cadastro e na mudança de status, validação da data de adoção e filtro “meus cães”.

## ☁️ Publicação (produção)

Variáveis de ambiente suportadas: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`. Execute `python manage.py collectstatic` e sirva `media/` e `staticfiles/` pelo servidor web (ex.: Nginx) ou serviço de armazenamento.

## 📌 Próximos passos

- Validação do MVP com os protetores e ajustes de usabilidade
- Cadastro de lares temporários e interessados
- Geração automática de arte para stories do Instagram
- Publicação em servidor com PostgreSQL e armazenamento de imagens em nuvem

## 📄 Licença

Projeto acadêmico de extensão, disponibilizado sob a licença MIT.
