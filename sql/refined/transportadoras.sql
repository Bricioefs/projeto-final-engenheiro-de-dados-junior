-- Grão: 1 linha por transportadora. PK: transportadora_id.
SELECT
    CAST(limpar(shipperID) AS INTEGER) AS transportadora_id,
    limpar(companyName)                AS transportadora,
    limpar(phone)                      AS telefone
FROM raw.transportadoras
WHERE limpar(shipperID) IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY CAST(limpar(shipperID) AS INTEGER) ORDER BY companyName) = 1
