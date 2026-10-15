-- Patas de Brasília | Módulo 3 | SQLite
-- DDL gerado das migrations; sem dados pessoais ou banco local.
-- Inclui tabelas de infraestrutura do Django; omite o diário django_migrations.
-- Uso acadêmico em banco vazio. Na aplicação, use manage.py migrate.
PRAGMA foreign_keys = ON;

BEGIN;

CREATE TABLE "animais_cao" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nome" varchar(60) NOT NULL,
    "sexo" varchar(1) NOT NULL,
    "porte" varchar(1) NOT NULL,
    "faixa_etaria" varchar(10) NOT NULL,
    "idade_aproximada" varchar(40) NOT NULL,
    "localizacao" varchar(100) NOT NULL,
    "castrado" bool NOT NULL,
    "vacinado" bool NOT NULL,
    "vermifugado" bool NOT NULL,
    "saude" text NOT NULL,
    "comportamento" text NOT NULL,
    "descricao" text NOT NULL,
    "observacoes_internas" text NOT NULL,
    "foto" varchar(100) NOT NULL,
    "status" varchar(20) NOT NULL,
    "data_adocao" date NULL,
    "criado_em" datetime NOT NULL,
    "atualizado_em" datetime NOT NULL,
    "protetor_id" bigint NOT NULL REFERENCES "animais_protetor" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "animais_configuracaosite" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "nome_projeto" varchar(80) NOT NULL,
    "slogan" varchar(160) NOT NULL,
    "sobre" text NOT NULL,
    "chave_pix" varchar(120) NOT NULL,
    "favorecido_pix" varchar(120) NOT NULL,
    "instagram" varchar(60) NOT NULL,
    "whatsapp_geral" varchar(20) NOT NULL,
    "email" varchar(254) NOT NULL
);

CREATE TABLE "animais_fotocao" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "imagem" varchar(100) NOT NULL,
    "enviada_em" datetime NOT NULL,
    "cao_id" bigint NOT NULL REFERENCES "animais_cao" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "animais_historicostatus" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "status_anterior" varchar(20) NOT NULL,
    "status_novo" varchar(20) NOT NULL,
    "observacao" varchar(255) NOT NULL,
    "criado_em" datetime NOT NULL,
    "autor_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "cao_id" bigint NOT NULL REFERENCES "animais_cao" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "animais_protetor" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "whatsapp" varchar(20) NOT NULL,
    "regiao" varchar(80) NOT NULL,
    "usuario_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "auth_group" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "name" varchar(150) NOT NULL UNIQUE
);

CREATE TABLE "auth_group_permissions" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "auth_permission" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "content_type_id" integer NOT NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "codename" varchar(100) NOT NULL,
    "name" varchar(255) NOT NULL
);

CREATE TABLE "auth_user" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "password" varchar(128) NOT NULL,
    "last_login" datetime NULL,
    "is_superuser" bool NOT NULL,
    "username" varchar(150) NOT NULL UNIQUE,
    "last_name" varchar(150) NOT NULL,
    "email" varchar(254) NOT NULL,
    "is_staff" bool NOT NULL,
    "is_active" bool NOT NULL,
    "date_joined" datetime NOT NULL,
    "first_name" varchar(150) NOT NULL
);

CREATE TABLE "auth_user_groups" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "auth_user_user_permissions" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "django_admin_log" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "object_id" text NULL,
    "object_repr" varchar(200) NOT NULL,
    "action_flag" smallint unsigned NOT NULL CHECK ("action_flag" >= 0),
    "change_message" text NOT NULL,
    "content_type_id" integer NULL REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
    "action_time" datetime NOT NULL
);

CREATE TABLE "django_content_type" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "app_label" varchar(100) NOT NULL,
    "model" varchar(100) NOT NULL
);

CREATE TABLE "django_session" (
    "session_key" varchar(40) NOT NULL PRIMARY KEY,
    "session_data" text NOT NULL,
    "expire_date" datetime NOT NULL
);

CREATE INDEX "animais_cao_protetor_id_097d7d20" ON "animais_cao" ("protetor_id");

CREATE INDEX "animais_fotocao_cao_id_79acf0c5" ON "animais_fotocao" ("cao_id");

CREATE INDEX "animais_historicostatus_autor_id_a4d34d9b" ON "animais_historicostatus" ("autor_id");

CREATE INDEX "animais_historicostatus_cao_id_9525f190" ON "animais_historicostatus" ("cao_id");

CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");

CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");

CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");

CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");

CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");

CREATE INDEX "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");

CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");

CREATE UNIQUE INDEX "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" ("user_id", "group_id");

CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");

CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");

CREATE UNIQUE INDEX "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" ("user_id", "permission_id");

CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");

CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");

CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");

CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");

COMMIT;
