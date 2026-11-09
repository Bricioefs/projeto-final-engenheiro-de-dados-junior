-- Pergunta: quais produtos mais faturam?
-- Grão: 1 linha por produto (top 20 por receita).
SELECT
    pr.produto,
    c.categoria,
    sum(i.quantidade)        AS unidades,
    sum(i.valor_liquido)     AS receita_liquida,
    sum(i.valor_desconto)    AS desconto_concedido
FROM refined.itens_pedido AS i
JOIN refined.produtos AS pr ON pr.produto_id = i.produto_id
LEFT JOIN refined.categorias AS c ON c.categoria_id = pr.categoria_id
GROUP BY 1, 2
ORDER BY receita_liquida DESC
LIMIT 20
