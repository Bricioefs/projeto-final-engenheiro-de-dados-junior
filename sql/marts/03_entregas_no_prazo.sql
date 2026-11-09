-- Pergunta: quantos pedidos enviados saíram até a data prevista?
-- Grão: 1 linha (resumo). Pedidos sem data de envio ficam fora (ainda não enviados).
SELECT
    count(*)                                                        AS pedidos_enviados,
    count(*) FILTER (WHERE data_envio <= data_prevista)             AS no_prazo,
    count(*) FILTER (WHERE data_envio > data_prevista)              AS atrasados,
    round(100.0 * count(*) FILTER (WHERE data_envio <= data_prevista) / count(*), 1) AS pct_no_prazo,
    round(avg(data_envio - data_pedido), 1)                         AS dias_medios_ate_envio
FROM refined.pedidos
WHERE data_envio IS NOT NULL
