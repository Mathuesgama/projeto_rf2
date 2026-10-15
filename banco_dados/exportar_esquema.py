"""Exporta somente o DDL das migrations em um banco temporário em memória."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
from django.conf import settings

settings.DATABASES["default"]["NAME"] = ":memory:"
django.setup()

from django.core.management import call_command
from django.db import connection

call_command("migrate", verbosity=0)
with connection.cursor() as cursor:
    cursor.execute(
        "SELECT sql FROM sqlite_master WHERE sql IS NOT NULL "
        "AND type IN ('table', 'index') AND name NOT LIKE 'sqlite_%' "
        "AND tbl_name != 'django_migrations' "
        "ORDER BY CASE type WHEN 'table' THEN 0 ELSE 1 END, name"
    )
    statements = [row[0] for row in cursor.fetchall()]

header = (
    "-- Patas de Brasília | Módulo 3 | SQLite\n"
    "-- DDL gerado das migrations; sem dados pessoais ou banco local.\n"
    "-- Inclui tabelas de infraestrutura do Django; omite o diário django_migrations.\n"
    "-- Uso acadêmico em banco vazio. Na aplicação, use manage.py migrate.\n"
    "PRAGMA foreign_keys = ON;\n\nBEGIN;\n\n"
)
def formatar(statement):
    if statement.startswith("CREATE TABLE"):
        inicio, _, corpo = statement.partition("(")
        return inicio + "(\n    " + corpo[:-1].replace(', "', ',\n    "') + "\n);"
    return statement + ";"


sql = header + "\n\n".join(formatar(s) for s in statements) + "\n\nCOMMIT;\n"
destino = Path(__file__).with_name("01_esquema.sql")
destino.write_text(sql, encoding="utf-8")
print(f"Esquema exportado: {destino.name} ({len(statements)} comandos DDL).")
