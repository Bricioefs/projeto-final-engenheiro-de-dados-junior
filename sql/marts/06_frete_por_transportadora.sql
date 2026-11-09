-- Pergunta: quanto pagamos de frete por transportadora e quanto ela demora?
-- Grão: 1 linha por transportadora. Frete está no pedido (não somar no nível de item).
SELECT
    t.transportadora,
    count(*)                                          AS pedidos,
    sum(p.valor_frete)                                AS frete_total,
    round(avg(p.valor_frete), 2)                      AS frete_medio,
    round(avg(p.data_envio - p.data_pedido), 1)       AS dias_medios_ate_envio,
    count(*) FILTER (WHERE p.data_envio > p.data_prevista) AS envios_atrasados
FROM refined.pedidos AS p
JOIN refined.transportadoras AS t ON t.transportadora_id = p.transportadora_id
GROUP BY 1
ORDER BY frete_total DESC
