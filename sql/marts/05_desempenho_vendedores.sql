-- Pergunta: quanto cada vendedor vendeu e qual a sua posição no ranking?
-- Grão: 1 linha por vendedor.
SELECT
    v.vendedor,
    v.cargo,
    count(DISTINCT p.pedido_id)                                 AS pedidos,
    count(DISTINCT p.cliente_id)                                AS clientes_atendidos,
    sum(i.valor_liquido)                                        AS receita_liquida,
    rank() OVER (ORDER BY sum(i.valor_liquido) DESC)            AS ranking
FROM refined.pedidos AS p
JOIN refined.itens_pedido AS i ON i.pedido_id = p.pedido_id
JOIN refined.vendedores AS v ON v.vendedor_id = p.vendedor_id
GROUP BY 1, 2
ORDER BY ranking
