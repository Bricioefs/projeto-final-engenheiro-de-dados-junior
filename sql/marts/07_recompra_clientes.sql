-- Pergunta: quantos clientes voltaram a comprar?
-- Grão: 1 linha por faixa de quantidade de pedidos por cliente.
WITH pedidos_cliente AS (
    SELECT cliente_id, count(*) AS pedidos
    FROM refined.pedidos
    GROUP BY 1
),
faixas AS (
    SELECT
        CASE
            WHEN pedidos = 1 THEN '1 pedido'
            WHEN pedidos BETWEEN 2 AND 5 THEN '2 a 5 pedidos'
            WHEN pedidos BETWEEN 6 AND 10 THEN '6 a 10 pedidos'
            ELSE 'mais de 10 pedidos'
        END AS faixa,
        CASE
            WHEN pedidos = 1 THEN 1
            WHEN pedidos BETWEEN 2 AND 5 THEN 2
            WHEN pedidos BETWEEN 6 AND 10 THEN 3
            ELSE 4
        END AS ordem
    FROM pedidos_cliente
)
SELECT
    faixa,
    count(*)                                              AS clientes,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1)    AS pct_clientes
FROM faixas
GROUP BY faixa, ordem
ORDER BY ordem
