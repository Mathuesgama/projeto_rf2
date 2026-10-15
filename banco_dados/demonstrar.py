"""Executa e verifica o roteiro SQL em memória, sem alterar db.sqlite3.

Uso: python banco_dados/demonstrar.py
Requer apenas a biblioteca padrão do Python.
"""
import sqlite3
from pathlib import Path

PASTA = Path(__file__).resolve().parent


def verificar(condicao, descricao):
    if not condicao:
        raise AssertionError(descricao)
    print(f"OK | {descricao}")


def consultas(conexao):
    script = (PASTA / "03_consultas.sql").read_text(encoding="utf-8")
    for numero, comando in enumerate(script.split(";"), 1):
        if not comando.strip():
            continue
        cursor = conexao.execute(comando)
        print(f"Q{numero} | " + " | ".join(col[0] for col in cursor.description))
        for linha in cursor.fetchall():
            print("     " + " | ".join(str(v) for v in linha))


def deve_rejeitar(conexao, sql, descricao):
    try:
        conexao.execute("BEGIN")
        conexao.execute(sql)
        # As FKs geradas pelo Django são diferidas até o COMMIT.
        conexao.commit()
    except sqlite3.IntegrityError:
        conexao.rollback()
        print(f"OK | {descricao}")
    else:
        conexao.rollback()
        raise AssertionError(f"Restrição não aplicada: {descricao}")


def main():
    with sqlite3.connect(":memory:") as conexao:
        for nome in ("01_esquema.sql", "02_dados.sql"):
            conexao.executescript((PASTA / nome).read_text(encoding="utf-8"))
        print("PATAS DE BRASÍLIA | DEMONSTRAÇÃO SQL DO MÓDULO 3")
        print("Execução isolada em memória; dados fictícios.\n")
        contar = lambda tabela: conexao.execute(f'SELECT COUNT(*) FROM "{tabela}"').fetchone()[0]
        verificar(conexao.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "Chaves estrangeiras ativas")
        for tabela, total in (("auth_user", 2), ("animais_protetor", 2),
                              ("animais_cao", 4), ("animais_fotocao", 2),
                              ("animais_historicostatus", 5), ("animais_configuracaosite", 1)):
            verificar(contar(tabela) == total, f"INSERT: {tabela} = {total}")
        print("\nCONSULTAS ANTES DA MANIPULAÇÃO")
        consultas(conexao)
        conexao.executescript((PASTA / "04_manipulacao.sql").read_text(encoding="utf-8"))
        print("\nVERIFICAÇÕES DA MANIPULAÇÃO")
        verificar(conexao.execute("SELECT status, data_adocao FROM animais_cao WHERE id=1").fetchone()
                  == ("adotado", "2026-10-15"), "UPDATE: Paçoca adotado em 15/10/2026")
        verificar(contar("animais_historicostatus") == 6, "INSERT: histórico passou de 5 para 6 registros")
        verificar(contar("animais_fotocao") == 1 and contar("animais_cao") == 4,
                  "DELETE: fotos de 2 para 1; os 4 cães foram preservados")
        # ROLLBACK restaura tanto o cão quanto o histórico em uma alteração abortada.
        conexao.execute("BEGIN")
        conexao.execute("UPDATE animais_cao SET status='tratamento' WHERE id=3")
        conexao.execute("DELETE FROM animais_historicostatus WHERE cao_id=3")
        conexao.rollback()
        verificar(conexao.execute("SELECT status FROM animais_cao WHERE id=3").fetchone()[0] == "lar_temporario"
                  and contar("animais_historicostatus") == 6, "ROLLBACK: situação e histórico restaurados")
        deve_rejeitar(conexao, "INSERT INTO animais_protetor (whatsapp,regiao,usuario_id) VALUES ('','','1')",
                      "UNIQUE: um perfil de protetor por usuário")
        deve_rejeitar(conexao, "UPDATE animais_cao SET protetor_id=999 WHERE id=1",
                      "FOREIGN KEY: responsável inexistente rejeitado")
        deve_rejeitar(conexao, "UPDATE animais_cao SET nome=NULL WHERE id=1",
                      "NOT NULL: nome nulo rejeitado")
        deve_rejeitar(conexao, "UPDATE animais_cao SET id=2 WHERE id=1",
                      "PRIMARY KEY: identificador duplicado rejeitado")
        deve_rejeitar(conexao, "DELETE FROM animais_protetor WHERE id=1",
                      "FOREIGN KEY: protetor com cães não pode ser removido por SQL direto")
        verificar(conexao.execute("PRAGMA foreign_key_check").fetchall() == [], "Nenhuma violação referencial")
        verificar(conexao.execute("PRAGMA integrity_check").fetchone()[0] == "ok", "Integridade SQLite: ok")
        print("\nCONSULTAS APÓS A MANIPULAÇÃO")
        consultas(conexao)
        print("\nRESULTADO: roteiro concluído com sucesso.")


if __name__ == "__main__":
    main()
