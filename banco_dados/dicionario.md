# Dicionário de dados

Tipos físicos do SQLite obtidos dos modelos Django 5.2. Campos textuais opcionais usam string vazia; apenas campos marcados como anuláveis aceitam SQL NULL. `max_length` e `choices` são validações da aplicação.

## User — `auth_user`

| Coluna | Tipo físico | Aceita NULL | Restrições e domínio |
|---|---|---|---|
| `id` | `integer` | Não | PK |
| `password` | `varchar(128)` | Não | — |
| `last_login` | `datetime` | Sim | — |
| `is_superuser` | `bool` | Não | — |
| `username` | `varchar(150)` | Não | UNIQUE |
| `first_name` | `varchar(150)` | Não | — |
| `last_name` | `varchar(150)` | Não | — |
| `email` | `varchar(254)` | Não | — |
| `is_staff` | `bool` | Não | — |
| `is_active` | `bool` | Não | — |
| `date_joined` | `datetime` | Não | — |

## Protetor — `animais_protetor`

| Coluna | Tipo físico | Aceita NULL | Restrições e domínio |
|---|---|---|---|
| `id` | `integer` | Não | PK |
| `usuario_id` | `integer` | Não | UNIQUE; FK → auth_user.id; ORM: CASCADE |
| `whatsapp` | `varchar(20)` | Não | — |
| `regiao` | `varchar(80)` | Não | — |

## Cao — `animais_cao`

| Coluna | Tipo físico | Aceita NULL | Restrições e domínio |
|---|---|---|---|
| `id` | `integer` | Não | PK |
| `nome` | `varchar(60)` | Não | — |
| `sexo` | `varchar(1)` | Não | choices: M, F |
| `porte` | `varchar(1)` | Não | choices: P, M, G |
| `faixa_etaria` | `varchar(10)` | Não | choices: filhote, adulto, idoso |
| `idade_aproximada` | `varchar(40)` | Não | — |
| `localizacao` | `varchar(100)` | Não | — |
| `protetor_id` | `bigint` | Não | FK → animais_protetor.id; ORM: PROTECT |
| `castrado` | `bool` | Não | — |
| `vacinado` | `bool` | Não | — |
| `vermifugado` | `bool` | Não | — |
| `saude` | `text` | Não | — |
| `comportamento` | `text` | Não | — |
| `descricao` | `text` | Não | — |
| `observacoes_internas` | `text` | Não | — |
| `foto` | `varchar(100)` | Não | Caminho do arquivo de mídia |
| `status` | `varchar(20)` | Não | choices: tratamento, lar_temporario, disponivel, em_adocao, adotado |
| `data_adocao` | `date` | Sim | Exigida pelos formulários quando adotado |
| `criado_em` | `datetime` | Não | — |
| `atualizado_em` | `datetime` | Não | — |

## FotoCao — `animais_fotocao`

| Coluna | Tipo físico | Aceita NULL | Restrições e domínio |
|---|---|---|---|
| `id` | `integer` | Não | PK |
| `cao_id` | `bigint` | Não | FK → animais_cao.id; ORM: CASCADE |
| `imagem` | `varchar(100)` | Não | Caminho do arquivo de mídia |
| `enviada_em` | `datetime` | Não | — |

## HistoricoStatus — `animais_historicostatus`

| Coluna | Tipo físico | Aceita NULL | Restrições e domínio |
|---|---|---|---|
| `id` | `integer` | Não | PK |
| `cao_id` | `bigint` | Não | FK → animais_cao.id; ORM: CASCADE |
| `status_anterior` | `varchar(20)` | Não | choices: tratamento, lar_temporario, disponivel, em_adocao, adotado |
| `status_novo` | `varchar(20)` | Não | choices: tratamento, lar_temporario, disponivel, em_adocao, adotado |
| `observacao` | `varchar(255)` | Não | — |
| `autor_id` | `integer` | Sim | FK → auth_user.id; ORM: SET_NULL |
| `criado_em` | `datetime` | Não | — |

## ConfiguracaoSite — `animais_configuracaosite`

| Coluna | Tipo físico | Aceita NULL | Restrições e domínio |
|---|---|---|---|
| `id` | `integer` | Não | PK |
| `nome_projeto` | `varchar(80)` | Não | — |
| `slogan` | `varchar(160)` | Não | — |
| `sobre` | `text` | Não | — |
| `chave_pix` | `varchar(120)` | Não | — |
| `favorecido_pix` | `varchar(120)` | Não | — |
| `instagram` | `varchar(60)` | Não | — |
| `whatsapp_geral` | `varchar(20)` | Não | — |
| `email` | `varchar(254)` | Não | — |

## Cardinalidades e normalização

- Usuário 1 : 0..1 Protetor; cada perfil exige exatamente um usuário.
- Protetor 1 : 0..N Cão; cada cão exige exatamente um responsável.
- Cão 1 : 0..N FotoCao e 1 : 0..N HistoricoStatus.
- Usuário 0..1 : 0..N HistoricoStatus; cada evento tem zero ou um autor.
- ConfiguracaoSite não possui relacionamentos; `save()` fixa a PK em 1.

Os atributos são atômicos no escopo do MVP (1FN). As chaves simples evitam dependências parciais (2FN). Dados do usuário e do protetor são separados dos cães; fotos e eventos têm tabelas próprias, evitando dependências transitivas no cadastro principal (3FN). A idade aproximada é uma descrição; o status atual repete o último estado do histórico para facilitar a consulta e precisa ser mantido consistente.

As demais tabelas do DDL são infraestrutura do Django (grupos, permissões, sessões, tipos de conteúdo e log administrativo); não representam novos módulos de negócio.
