-- Pergunta: como está o negócio em um olhar? (cartões do dashboard)
-- Grão: 1 linha (resumo geral).
WITH valor_pedido AS (
    SELECT pedido_id, sum(valor_liquido) AS valor
    FROM refined.itens_pedido
    GROUP BY 1
)
SELECT
    (SELECT sum(valor) FROM valor_pedido)                              AS receita_liquida,
    (SELECT count(*) FROM refined.pedidos)                             AS pedidos,
    (SELECT round(avg(valor), 2) FROM valor_pedido)                    AS ticket_medio,
    (SELECT count(DISTINCT cliente_id) FROM refined.pedidos)           AS clientes_ativos,
    (SELECT sum(valor_frete) FROM refined.pedidos)                     AS frete_total,
    (SELECT round(100.0 * count(*) FILTER (WHERE data_envio <= data_prevista) / count(*), 1)
       FROM refined.pedidos WHERE data_envio IS NOT NULL)              AS pct_no_prazo,
    (SELECT count(*) FROM refined.pedidos WHERE data_envio IS NULL)    AS pedidos_nao_enviados
