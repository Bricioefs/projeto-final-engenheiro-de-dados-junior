-- Grão: 1 linha por produto. PK: produto_id. FKs: fornecedor_id, categoria_id.
SELECT
    CAST(limpar(productID) AS INTEGER)        AS produto_id,
    limpar(productName)                       AS produto,
    CAST(limpar(supplierID) AS INTEGER)       AS fornecedor_id,
    CAST(limpar(categoryID) AS INTEGER)       AS categoria_id,
    limpar(quantityPerUnit)                   AS embalagem,
    CAST(limpar(unitPrice) AS DECIMAL(12, 2)) AS preco_tabela,
    CAST(limpar(unitsInStock) AS INTEGER)     AS estoque,
    CAST(limpar(unitsOnOrder) AS INTEGER)     AS em_pedido_compra,
    CAST(limpar(reorderLevel) AS INTEGER)     AS ponto_reposicao,
    limpar(discontinued) = '1'                AS descontinuado
FROM raw.produtos
WHERE limpar(productID) IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY CAST(limpar(productID) AS INTEGER) ORDER BY productName) = 1
