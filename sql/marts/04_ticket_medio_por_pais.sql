-- Pergunta: qual o ticket médio por país do cliente?
-- Grão: 1 linha por país. Primeiro soma por pedido (CTE) para não distorcer a média pelos itens.
WITH valor_pedido AS (
    SELECT p.pedido_id, cl.pais, sum(i.valor_liquido) AS valor
    FROM refined.pedidos AS p
    JOIN refined.itens_pedido AS i ON i.pedido_id = p.pedido_id
    JOIN refined.clientes AS cl ON cl.cliente_id = p.cliente_id
    GROUP BY 1, 2
)
SELECT
    pais,
    count(*)                 AS pedidos,
    sum(valor)               AS receita_liquida,
    round(avg(valor), 2)     AS ticket_medio
FROM valor_pedido
GROUP BY 1
ORDER BY receita_liquida DESC
