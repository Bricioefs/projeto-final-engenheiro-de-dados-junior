-- Pergunta: quanto da receita bruta foi cedido em descontos, ano a ano?
-- Grão: 1 linha por ano do pedido.
SELECT
    year(p.data_pedido)                                            AS ano,
    sum(i.valor_bruto)                                             AS receita_bruta,
    sum(i.valor_desconto)                                          AS descontos,
    sum(i.valor_liquido)                                           AS receita_liquida,
    round(100 * sum(i.valor_desconto) / sum(i.valor_bruto), 2)     AS pct_desconto
FROM refined.pedidos AS p
JOIN refined.itens_pedido AS i ON i.pedido_id = p.pedido_id
GROUP BY 1
ORDER BY 1
