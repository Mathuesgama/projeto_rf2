# Banco de dados — Módulo 3

Continuidade do **Patas de Brasília**, implementado no Módulo 2 para os requisitos RF01–RF08. O esquema permanece o das migrations existentes; a atividade acrescenta sua representação SQL, o modelo relacional e uma demonstração reproduzível.

## Executar a demonstração

Na raiz do repositório, com Python 3.12 ou superior:

```console
python banco_dados/demonstrar.py
```

O roteiro usa somente a biblioteca padrão do Python e um banco SQLite **em memória**. Cria as tabelas, insere dados fictícios, executa cinco consultas antes e depois da manipulação e verifica atualização, exclusão, rollback e restrições. Não acessa `db.sqlite3`, não cria contas na aplicação e não depende de servidor SQLite.

Saída de referência: [evidencias_sql.txt](evidencias_sql.txt). O comando termina com erro se uma verificação falhar.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| `01_esquema.sql` | DDL das migrations: 14 tabelas e 19 índices explícitos; sem dados e sem o diário `django_migrations` |
| `02_dados.sql` | INSERT de 2 usuários, 2 protetores, 4 cães, 2 fotos, 5 eventos e 1 configuração fictícios |
| `03_consultas.sql` | SELECT com JOIN, LEFT JOIN, filtros, ordenação, COUNT e GROUP BY |
| `04_manipulacao.sql` | Atualização de adoção com histórico na mesma transação; remoção de uma foto duplicada |
| `demonstrar.py` | Execução isolada dos SQL e verificações de integridade |
| `exportar_esquema.py` | Reconstrução do DDL a partir das migrations, em memória; requer as dependências do projeto |
| `modelo.mmd`, `modelo.svg`, `modelo.png` | Diagrama dos cinco modelos de domínio e do usuário Django |
| `dicionario.md` | Campos físicos, tipos, nulabilidade e relacionamentos |

Para examinar os scripts em um cliente SQLite, abra **um banco vazio separado** e execute os arquivos `01`, `02`, `03` e `04` nessa ordem. Execute `03` novamente para comparar os resultados. Os caminhos de imagem são ilustrativos e não geram arquivos de mídia.

## Relação com a aplicação

Na aplicação, continue utilizando `python manage.py migrate` e o comando `popular_dados` documentado no README principal. O DDL acadêmico omite o diário de migrations e os dados de permissões criados pelo Django; não substitui a inicialização normal da aplicação.

Para atualizar o arquivo SQL após mudanças nas migrations:

```console
python banco_dados/exportar_esquema.py
python banco_dados/demonstrar.py
```

## Regras e limites do modelo atual

- Toda entidade de domínio tem chave primária `id`. `Protetor.usuario_id` tem `UNIQUE` e FK para `auth_user`, permitindo no máximo um perfil por usuário.
- Cada cão exige um protetor existente. Fotos e eventos exigem um cão existente. O autor de um evento pode ser nulo.
- `CASCADE`, `PROTECT` e `SET_NULL` configurados em `models.py` são comportamentos executados pelo ORM do Django. O DDL SQLite exportado usa referências diferidas com `NO ACTION`; SQL direto precisa tratar os dependentes explicitamente.
- As opções de sexo, porte, faixa etária e situação são validadas nos formulários/modelos. Não existem `CHECK` de domínio nessas tabelas. O SQLite também não impõe os limites de `varchar(n)` como um SGBD de tipagem rígida.
- A exigência de data para adoção está em `CaoForm` e `StatusForm`. A configuração única é mantida pelo método `save()` de `ConfiguracaoSite`, que fixa `id=1`; não é uma restrição física contra SQL direto.
- Arquivos de foto ficam no armazenamento de mídia; o banco guarda seus caminhos. Remover um registro por SQL não remove o arquivo do disco.
- O histórico representa as transições; `Cao.status` mantém a situação atual para as consultas. Atualizações SQL diretas precisam gravar o histórico explicitamente.
- A consulta pública seleciona apenas os campos necessários. A autorização continua na aplicação; o SQLite não oferece usuários e permissões por tabela como um servidor PostgreSQL.

## Verificações realizadas

O roteiro confirma os totais de inserção, mudança de situação e data, novo histórico, remoção de foto sem remover cães, rollback e rejeição de PK duplicada, usuário com perfil duplicado, nome nulo, responsável inexistente e remoção de protetor com cães. Ao final, `foreign_key_check` não retorna violações e `integrity_check` retorna `ok`.

Os nove testes da aplicação são executados separadamente:

```console
python manage.py test animais
```

## Versionamento

Repositório: https://github.com/Mathuesgama/projeto_rf2

As entregas do módulo são registradas em commits por etapa: SQL verificável; modelagem e documentação; relatório acadêmico. O histórico anterior já contém desenvolvimento, correções, evolução dos dados de demonstração e um merge (`d341e4c`). Nesta entrega, os incrementos são feitos em `main`; não se afirma a utilização de branches de funcionalidade ou pull requests que não ocorreram.

Não versionar banco local, mídia de usuários ou ambiente virtual. Consultar o histórico com `git log --oneline --graph --all` e revisar alterações com `git diff` antes de cada commit.
