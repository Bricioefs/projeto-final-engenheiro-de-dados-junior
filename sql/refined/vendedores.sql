-- Grão: 1 linha por vendedor. PK: vendedor_id. FK: gestor_id (auto-relacionamento).
-- Colunas pessoais desnecessárias para análise (endereço, telefone, foto, notas) ficam fora.
SELECT
    CAST(limpar(employeeID) AS INTEGER)                    AS vendedor_id,
    limpar(firstName) || ' ' || limpar(lastName)           AS vendedor,
    limpar(title)                                          AS cargo,
    CAST(TRY_CAST(limpar(hireDate) AS TIMESTAMP) AS DATE)  AS data_admissao,
    limpar(city)                                           AS cidade,
    limpar(country)                                        AS pais,
    CAST(limpar(reportsTo) AS INTEGER)                     AS gestor_id
FROM raw.vendedores
WHERE limpar(employeeID) IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY CAST(limpar(employeeID) AS INTEGER) ORDER BY lastName) = 1
