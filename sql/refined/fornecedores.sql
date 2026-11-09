-- Grão: 1 linha por fornecedor. PK: fornecedor_id.
SELECT
    CAST(limpar(supplierID) AS INTEGER) AS fornecedor_id,
    limpar(companyName)                 AS razao_social,
    limpar(city)                        AS cidade,
    limpar(region)                      AS regiao,
    limpar(country)                     AS pais
FROM raw.fornecedores
WHERE limpar(supplierID) IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY CAST(limpar(supplierID) AS INTEGER) ORDER BY companyName) = 1
