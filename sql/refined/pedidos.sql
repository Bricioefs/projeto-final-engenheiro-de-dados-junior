-- Grão: 1 linha por pedido. PK: pedido_id. FKs: cliente_id, vendedor_id, transportadora_id.
SELECT
    CAST(limpar(orderID) AS INTEGER)                       AS pedido_id,
    upper(limpar(customerID))                              AS cliente_id,
    CAST(limpar(employeeID) AS INTEGER)                    AS vendedor_id,
    CAST(TRY_CAST(limpar(orderDate) AS TIMESTAMP) AS DATE)    AS data_pedido,
    CAST(TRY_CAST(limpar(requiredDate) AS TIMESTAMP) AS DATE) AS data_prevista,
    CAST(TRY_CAST(limpar(shippedDate) AS TIMESTAMP) AS DATE)  AS data_envio,
    CAST(limpar(shipVia) AS INTEGER)                       AS transportadora_id,
    CAST(limpar(freight) AS DECIMAL(12, 2))                AS valor_frete,
    limpar(shipName)                                       AS destinatario,
    limpar(shipCity)                                       AS cidade_entrega,
    limpar(shipRegion)                                     AS regiao_entrega,
    limpar(shipPostalCode)                                 AS cep_entrega,
    limpar(shipCountry)                                    AS pais_entrega
FROM raw.pedidos
WHERE limpar(orderID) IS NOT NULL
QUALIFY row_number() OVER (PARTITION BY CAST(limpar(orderID) AS INTEGER) ORDER BY orderDate DESC) = 1
