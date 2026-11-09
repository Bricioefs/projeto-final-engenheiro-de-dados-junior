-- Grão: 1 linha por produto dentro de um pedido. PK: (pedido_id, produto_id). FKs: pedido_id, produto_id.
-- Valores derivados linha a linha (sem agregação): bruto, desconto e líquido.
WITH tipado AS (
    SELECT
        CAST(limpar(orderID) AS INTEGER)          AS pedido_id,
        CAST(limpar(productID) AS INTEGER)        AS produto_id,
        CAST(limpar(unitPrice) AS DECIMAL(12, 2)) AS preco_unitario,
        CAST(limpar(quantity) AS INTEGER)         AS quantidade,
        CAST(limpar(discount) AS DECIMAL(5, 4))   AS percentual_desconto
    FROM raw.itens_pedido
    WHERE limpar(orderID) IS NOT NULL AND limpar(productID) IS NOT NULL
)
SELECT
    pedido_id,
    produto_id,
    preco_unitario,
    quantidade,
    percentual_desconto,
    CAST(preco_unitario * quantidade AS DECIMAL(14, 2))                         AS valor_bruto,
    CAST(preco_unitario * quantidade * percentual_desconto AS DECIMAL(14, 2))   AS valor_desconto,
    CAST(preco_unitario * quantidade * (1 - percentual_desconto) AS DECIMAL(14, 2)) AS valor_liquido
FROM tipado
WHERE quantidade > 0 AND preco_unitario >= 0
QUALIFY row_number() OVER (PARTITION BY pedido_id, produto_id ORDER BY quantidade DESC) = 1
