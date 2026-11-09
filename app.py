"""Dashboard em Streamlit que lê somente a camada marts.

Uso:
    uv run streamlit run app.py

Pergunta principal: as vendas estão crescendo e o serviço (prazo/frete) acompanha?
Público: gestão comercial — leitura rápida nos cartões, detalhe nos gráficos.
"""

from __future__ import annotations

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

from pipeline.config import CAMINHO_BANCO

COR = "#1f6feb"

st.set_page_config(page_title="Northwind | Vendas", page_icon="📦", layout="wide")


@st.cache_data(ttl=300)
def ler_mart(tabela: str) -> pd.DataFrame:
    """Lê uma tabela do schema marts em modo somente leitura."""
    with duckdb.connect(str(CAMINHO_BANCO), read_only=True) as conexao:
        return conexao.execute(f"SELECT * FROM marts.{tabela}").df()


def moeda(valor: float) -> str:
    """Formata no padrão brasileiro: US$ 1.234,56."""
    return "US$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def moeda_curta(valor: float) -> str:
    """Formata valores grandes de forma compacta para caber no cartão: US$ 1,27 mi."""
    if abs(valor) >= 1_000_000:
        return "US$ " + f"{valor / 1_000_000:.2f}".replace(".", ",") + " mi"
    return moeda(valor)


if not CAMINHO_BANCO.exists():
    st.error("Banco não encontrado. Rode antes: `uv run python -m pipeline --baixar`")
    st.stop()

st.title("📦 Northwind — Vendas, entregas e clientes")
st.caption("Fonte: base pública Northwind (1996–1998). Valores em dólar, líquidos de desconto.")

# ---------- Cartões: como está agora ----------
kpi = ler_mart("kpis_resumo").iloc[0]
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Receita líquida", moeda_curta(kpi.receita_liquida))
c2.metric("Pedidos", f"{int(kpi.pedidos):,}".replace(",", "."))
c3.metric("Ticket médio", moeda(kpi.ticket_medio))
c4.metric("Entregas no prazo", f"{kpi.pct_no_prazo:.1f}%".replace(".", ","))
c5.metric("Frete total", moeda(kpi.frete_total))

# ---------- Tendência ----------
st.subheader("Quanto vendemos por mês?")
vendas = ler_mart("vendas_mensais")
grafico = px.line(vendas, x="mes", y="receita_liquida", markers=True,
                  labels={"mes": "Mês", "receita_liquida": "Receita líquida"})
grafico.update_traces(line_color=COR)
st.plotly_chart(grafico, width="stretch")
st.caption("O último mês (maio/1998) está incompleto na base: a queda final não é tendência.")

# ---------- O que vende e quem vende ----------
esquerda, direita = st.columns(2)
with esquerda:
    st.subheader("Quais categorias mais vendem?")
    categorias = ler_mart("receita_por_categoria").sort_values("receita_liquida")
    st.plotly_chart(
        px.bar(categorias, x="receita_liquida", y="categoria", orientation="h",
               labels={"receita_liquida": "Receita líquida", "categoria": ""},
               color_discrete_sequence=[COR]),
        width="stretch",
    )
with direita:
    st.subheader("Ranking de vendedores")
    vendedores = ler_mart("desempenho_vendedores").sort_values("receita_liquida")
    st.plotly_chart(
        px.bar(vendedores, x="receita_liquida", y="vendedor", orientation="h",
               labels={"receita_liquida": "Receita líquida", "vendedor": ""},
               color_discrete_sequence=[COR]),
        width="stretch",
    )

# ---------- Clientes ----------
esquerda, direita = st.columns(2)
with esquerda:
    st.subheader("Ticket médio por país (top 10 em receita)")
    paises = ler_mart("ticket_medio_por_pais").head(10).sort_values("ticket_medio")
    st.plotly_chart(
        px.bar(paises, x="ticket_medio", y="pais", orientation="h",
               labels={"ticket_medio": "Ticket médio", "pais": ""},
               color_discrete_sequence=[COR]),
        width="stretch",
    )
with direita:
    st.subheader("Os clientes voltam a comprar?")
    recompra = ler_mart("recompra_clientes")
    st.plotly_chart(
        px.bar(recompra, x="faixa", y="clientes", text="pct_clientes",
               labels={"faixa": "Pedidos por cliente", "clientes": "Clientes"},
               color_discrete_sequence=[COR]).update_traces(texttemplate="%{text}%"),
        width="stretch",
    )

# ---------- Logística e descontos ----------
esquerda, direita = st.columns(2)
with esquerda:
    st.subheader("Frete e prazo por transportadora")
    st.dataframe(ler_mart("frete_por_transportadora"), hide_index=True, width="stretch")
    st.subheader("Descontos concedidos por ano")
    st.dataframe(ler_mart("descontos_por_ano"), hide_index=True, width="stretch")
with direita:
    st.subheader("Top 20 produtos")
    st.dataframe(ler_mart("top_produtos"), hide_index=True, width="stretch", height=420)
