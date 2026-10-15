PRAGMA foreign_keys = ON;
-- Uma transação mantém a mudança de situação e seu histórico juntos.
BEGIN;
INSERT INTO animais_historicostatus
    (status_anterior, status_novo, observacao, criado_em, autor_id, cao_id)
SELECT status, 'adotado', 'Termo fictício assinado', '2026-10-15 15:00:00', 1, id
FROM animais_cao WHERE id = 1 AND status = 'disponivel';

UPDATE animais_cao
SET status = 'adotado', data_adocao = '2026-10-15',
    atualizado_em = '2026-10-15 15:00:00'
WHERE id = 1 AND status = 'disponivel';

-- Remoção de um registro de foto duplicada, sem apagar o animal.
DELETE FROM animais_fotocao
WHERE id = 2 AND cao_id = 1 AND imagem = 'caes/extras/pacoca_duplicada.jpg';
COMMIT;
