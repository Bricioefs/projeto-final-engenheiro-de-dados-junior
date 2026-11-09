-- Pergunta: quais categorias mais vendem?
-- Grão: 1 linha por categoria.
SELECT
    coalesce(c.categoria, 'Sem categoria')                         AS categoria,
    count(DISTINCT i.pedido_id)                                    AS pedidos,
    sum(i.quantidade)                                              AS unidades,
    sum(i.valor_liquido)                                           AS receita_liquida,
    round(100 * sum(i.valor_liquido) / sum(sum(i.valor_liquido)) OVER (), 1) AS participacao_pct
FROM refined.itens_pedido AS i
JOIN refined.produtos AS pr ON pr.produto_id = i.produto_id
LEFT JOIN refined.categorias AS c ON c.categoria_id = pr.categoria_id
GROUP BY 1
ORDER BY receita_liquida DESC
