-- Grão: 1 linha por cliente. PK: cliente_id. CEP fica como texto (preserva zeros à esquerda).
SELECT
    upper(limpar(customerID)) AS cliente_id,
    limpar(companyName)       AS razao_social,
    limpar(contactName)       AS contato,
    limpar(contactTitle)      AS cargo_contato,
    limpar(city)              AS cidade,
    limpar(region)            AS regiao,
    limpar(postalCode)        AS cep,
    limpar(country)           AS pais
FROM raw.clientes
WHERE limpar(customerID) IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY upper(limpar(customerID)) ORDER BY companyName) = 1
