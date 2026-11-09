-- Pergunta: quanto vendemos por mês?
-- Grão: 1 linha por mês do pedido. Receita = valor líquido dos itens (já com desconto).
SELECT
    date_trunc('month', p.data_pedido)::DATE AS mes,
    count(DISTINCT p.pedido_id)              AS pedidos,
    sum(i.quantidade)                        AS unidades,
    sum(i.valor_liquido)                     AS receita_liquida
FROM refined.pedidos AS p
JOIN refined.itens_pedido AS i ON i.pedido_id = p.pedido_id
GROUP BY 1
ORDER BY 1
