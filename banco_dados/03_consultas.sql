-- Q1: vitrine pública, com projeção explícita sem observações internas.
SELECT c.id, c.nome, c.status, u.first_name AS protetor, c.localizacao
FROM animais_cao AS c
JOIN animais_protetor AS p ON p.id = c.protetor_id
JOIN auth_user AS u ON u.id = p.usuario_id
WHERE c.status IN ('lar_temporario', 'disponivel', 'em_adocao')
ORDER BY c.nome;

-- Q2: carga de acompanhamento, inclusive protetores sem cães ativos.
SELECT u.first_name AS protetor, COUNT(c.id) AS caes_nao_adotados
FROM animais_protetor AS p
JOIN auth_user AS u ON u.id = p.usuario_id
LEFT JOIN animais_cao AS c ON c.protetor_id = p.id AND c.status <> 'adotado'
GROUP BY p.id, u.first_name
ORDER BY p.id;

-- Q3: histórico cronológico do cão 1, preservando autor opcional.
SELECT c.nome, h.status_anterior, h.status_novo, h.criado_em,
       COALESCE(u.first_name, 'Autor removido') AS autor
FROM animais_historicostatus AS h
JOIN animais_cao AS c ON c.id = h.cao_id
LEFT JOIN auth_user AS u ON u.id = h.autor_id
WHERE c.id = 1
ORDER BY h.criado_em, h.id;

-- Q4: animais adotados (página de finais felizes).
SELECT nome, data_adocao FROM animais_cao
WHERE status = 'adotado'
ORDER BY data_adocao DESC, id;

-- Q5: resumo por situação para o painel interno.
SELECT status, COUNT(*) AS quantidade FROM animais_cao
GROUP BY status ORDER BY status;
