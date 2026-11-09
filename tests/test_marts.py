"""Testes da camada marts (pipeline.marts) e do pipeline completo com dados inventados."""

from __future__ import annotations

from decimal import Decimal

import duckdb
import pytest

from pipeline.ingestao import executar_ingestao
from pipeline.marts import executar_marts, ler_arquivos_marts
from pipeline.transformacao import executar_transformacao


@pytest.fixture
def banco_marts(pasta_raw, caminho_banco):
    executar_ingestao(pasta_raw, caminho_banco)
    executar_transformacao(caminho_banco)
    executar_marts(caminho_banco)
    return caminho_banco


def consultar(caminho, sql):
    with duckdb.connect(str(caminho), read_only=True) as conexao:
        return conexao.execute(sql).fetchall()


# ---------- leitura e validação dos arquivos ----------

def test_le_em_ordem_numerica(tmp_path):
    (tmp_path / "02_b.sql").write_text("SELECT 2", encoding="utf-8")
    (tmp_path / "01_a.sql").write_text("SELECT 1;", encoding="utf-8")

    marts = ler_arquivos_marts(tmp_path)

    assert [m.tabela for m in marts] == ["a", "b"]
    assert marts[0].consulta == "SELECT 1"  # ';' final é removido


@pytest.mark.parametrize(
    ("nome", "conteudo", "erro"),
    [
        ("1_curto.sql", "SELECT 1", "Nome inválido"),
        ("01_Maiusculo.sql", "SELECT 1", "Nome inválido"),
        ("01_vazio.sql", "  ", "vazio"),
        ("01_dois.sql", "SELECT 1; SELECT 2", "único SELECT"),
    ],
)
def test_recusa_arquivos_invalidos(tmp_path, nome, conteudo, erro):
    (tmp_path / nome).write_text(conteudo, encoding="utf-8")
    with pytest.raises(ValueError, match=erro):
        ler_arquivos_marts(tmp_path)


def test_recusa_ordem_repetida(tmp_path):
    (tmp_path / "01_a.sql").write_text("SELECT 1", encoding="utf-8")
    (tmp_path / "01_b.sql").write_text("SELECT 1", encoding="utf-8")
    with pytest.raises(ValueError, match="repetida"):
        ler_arquivos_marts(tmp_path)


def test_pasta_inexistente_ou_vazia(tmp_path):
    with pytest.raises(FileNotFoundError):
        ler_arquivos_marts(tmp_path / "nao_existe")
    with pytest.raises(FileNotFoundError):
        ler_arquivos_marts(tmp_path)


def test_falha_em_um_mart_desfaz_todos(caminho_banco, tmp_path):
    (tmp_path / "01_ok.sql").write_text("SELECT 1 AS x", encoding="utf-8")
    (tmp_path / "02_quebrado.sql").write_text("SELECT * FROM tabela_que_nao_existe", encoding="utf-8")

    with pytest.raises(duckdb.Error):
        executar_marts(caminho_banco, tmp_path)
    assert consultar(caminho_banco, "SELECT count(*) FROM duckdb_tables() WHERE schema_name = 'marts'") == [(0,)]


# ---------- indicadores reais sobre os dados inventados ----------

def test_gera_os_dez_marts(banco_marts):
    tabelas = consultar(banco_marts, "SELECT count(*) FROM duckdb_tables() WHERE schema_name = 'marts'")
    assert tabelas == [(10,)]


def test_kpis_resumo(banco_marts):
    # Pedido 1: 200 + 45 = 245 | Pedido 2: 100 | Pedido 3: 4 x 50 x 0,75 = 150 (duplicata removida)
    receita, pedidos, ticket, clientes, frete, pct_prazo, nao_enviados = consultar(
        banco_marts, "SELECT * FROM marts.kpis_resumo"
    )[0]
    assert receita == Decimal("495.00")
    assert pedidos == 3
    assert ticket == pytest.approx(165.0)
    assert clientes == 2
    assert frete == Decimal("35.50")
    assert pct_prazo == pytest.approx(50.0)  # 1 de 2 enviados no prazo
    assert nao_enviados == 1


def test_vendas_mensais_soma_igual_receita_total(banco_marts):
    meses = consultar(banco_marts, "SELECT mes, pedidos, receita_liquida FROM marts.vendas_mensais ORDER BY mes")
    assert [(m[1], m[2]) for m in meses] == [(2, Decimal("345.00")), (1, Decimal("150.00"))]


def test_entregas_no_prazo(banco_marts):
    assert consultar(banco_marts, "SELECT pedidos_enviados, no_prazo, atrasados FROM marts.entregas_no_prazo") == [
        (2, 1, 1)
    ]


def test_recompra_clientes(banco_marts):
    assert consultar(banco_marts, "SELECT faixa, clientes FROM marts.recompra_clientes") == [
        ("1 pedido", 1),
        ("2 a 5 pedidos", 1),
    ]


def test_ticket_medio_por_pais_nao_distorce_pelos_itens(banco_marts):
    linhas = dict(consultar(banco_marts, "SELECT pais, ticket_medio FROM marts.ticket_medio_por_pais"))
    assert linhas["Brazil"] == pytest.approx(172.5)  # (245 + 100) / 2 pedidos
    assert linhas["Germany"] == pytest.approx(150.0)
