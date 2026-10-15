-- Dados exclusivamente fictícios. Contas inativas e com senha inutilizável.
-- Caminhos de imagens são ilustrativos; este roteiro não copia arquivos de mídia.
PRAGMA foreign_keys = ON;
BEGIN;

INSERT INTO auth_user
    (id, password, last_login, is_superuser, username, first_name,
     last_name, email, is_staff, is_active, date_joined)
VALUES
    (1, '!', NULL, 0, 'ana_sql', 'Ana', 'Exemplo', '', 0, 0, '2026-10-15 12:00:00'),
    (2, '!', NULL, 0, 'bruno_sql', 'Bruno', 'Exemplo', '', 0, 0, '2026-10-15 12:00:00');

INSERT INTO animais_protetor (id, whatsapp, regiao, usuario_id)
VALUES (1, '61000000000', 'Asa Norte', 1),
       (2, '61000000001', 'Taguatinga', 2);

INSERT INTO animais_cao
    (id, nome, sexo, porte, faixa_etaria, idade_aproximada, localizacao,
     castrado, vacinado, vermifugado, saude, comportamento, descricao,
     observacoes_internas, foto, status, data_adocao, criado_em,
     atualizado_em, protetor_id)
VALUES
    (1, 'Paçoca', 'M', 'M', 'adulto', '2 anos', 'Asa Norte',
     1, 1, 1, 'Sem intercorrências', 'Sociável', 'Busca um lar responsável.',
     'Dado fictício interno', 'caes/pacoca.jpg', 'disponivel', NULL,
     '2026-10-15 12:00:00', '2026-10-15 12:00:00', 1),
    (2, 'Luna', 'F', 'P', 'filhote', '4 meses', 'Asa Norte',
     0, 0, 1, 'Em acompanhamento', 'Brincalhona', '',
     'Dado fictício interno', 'caes/luna.jpg', 'tratamento', NULL,
     '2026-10-15 12:00:00', '2026-10-15 12:00:00', 1),
    (3, 'Rex', 'M', 'G', 'adulto', '3 anos', 'Taguatinga',
     1, 1, 1, '', 'Tranquilo', 'Em lar temporário.',
     '', 'caes/rex.jpg', 'lar_temporario', NULL,
     '2026-10-15 12:00:00', '2026-10-15 12:00:00', 2),
    (4, 'Mel', 'F', 'M', 'adulto', '5 anos', 'Taguatinga',
     1, 1, 1, '', 'Dócil', 'Adoção concluída.',
     '', 'caes/mel.jpg', 'adotado', '2026-10-10',
     '2026-10-10 12:00:00', '2026-10-15 12:00:00', 2);

INSERT INTO animais_fotocao (id, imagem, enviada_em, cao_id)
VALUES (1, 'caes/extras/pacoca_1.jpg', '2026-10-15 12:00:00', 1),
       (2, 'caes/extras/pacoca_duplicada.jpg', '2026-10-15 12:00:00', 1);

INSERT INTO animais_historicostatus
    (id, status_anterior, status_novo, observacao, criado_em, autor_id, cao_id)
VALUES
    (1, '', 'tratamento', 'Cadastro fictício', '2026-10-14 12:00:00', 1, 1),
    (2, 'tratamento', 'disponivel', 'Liberado para divulgação', '2026-10-15 12:00:00', 1, 1),
    (3, '', 'tratamento', 'Cadastro fictício', '2026-10-15 12:00:00', 1, 2),
    (4, '', 'lar_temporario', 'Cadastro fictício', '2026-10-15 12:00:00', 2, 3),
    (5, 'em_adocao', 'adotado', 'Adoção fictícia concluída', '2026-10-10 12:00:00', 2, 4);

INSERT INTO animais_configuracaosite
    (id, nome_projeto, slogan, sobre, chave_pix, favorecido_pix,
     instagram, whatsapp_geral, email)
VALUES (1, 'Patas de Brasília', 'Adoção responsável que transforma vidas.',
        'Demonstração acadêmica com dados fictícios.', '', '', '', '', '');

COMMIT;
