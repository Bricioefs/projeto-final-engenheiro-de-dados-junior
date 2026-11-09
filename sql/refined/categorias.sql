-- Grão: 1 linha por categoria. PK: categoria_id. A coluna binária "picture" não é usada.
SELECT
    CAST(limpar(categoryID) AS INTEGER) AS categoria_id,
    limpar(categoryName)                AS categoria,
    limpar(description)                 AS descricao
FROM raw.categorias
WHERE limpar(categoryID) IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY CAST(limpar(categoryID) AS INTEGER) ORDER BY categoryName) = 1
