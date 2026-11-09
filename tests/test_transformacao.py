"""Testes da camada refined (pipeline.transformacao) usando os SQLs reais do projeto."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import duckdb
import pytest

from pipeline.ingestao import executar_ingestao
from pipeline.transformacao import ChaveDuplicadaError, executar_transformacao


@pytest.fixture
def banco_refined(pasta_raw, caminho_banco):
    executar_ingestao(pasta_raw, caminho_banco)
    executar_transformacao(caminho_banco)
    return caminho_banco


def consultar(caminho, sql):
    with duckdb.connect(str(caminho), read_only=True) as conexao:
        return conexao.execute(sql).fetchall()


def test_remove_item_duplicado(banco_refined):
    assert consultar(banco_refined, "SELECT count(*) FROM refined.itens_pedido") == [(4,)]


def test_tipagem_correta(banco_refined):
    tipos = dict(consultar(banco_refined, "SELECT column_name, column_type FROM (DESCRIBE refined.pedidos)"))
    assert tipos["pedido_id"] == "INTEGER"
    assert tipos["data_pedido"] == "DATE"
    assert tipos["valor_frete"].startswith("DECIMAL")


def test_texto_null_vira_nulo_de_verdade(banco_refined):
    linha = consultar(banco_refined, "SELECT data_envio, regiao_entrega FROM refined.pedidos WHERE pedido_id = 3")
    assert linha == [(None, None)]


def test_valores_derivados_do_item(banco_refined):
    linha = consultar(
        banco_refined,
        "SELECT valor_bruto, valor_desconto, valor_liquido FROM refined.itens_pedido "
        "WHERE pedido_id = 1 AND produto_id = 20",
    )
    assert linha == [(Decimal("50.00"), Decimal("5.00"), Decimal("45.00"))]


def test_padroniza_chave_do_cliente_e_preserva_cep(banco_refined):
    linhas = consultar(banco_refined, "SELECT cliente_id, cep FROM refined.clientes ORDER BY 1")
    assert linhas == [("AAA", "01310"), ("BBB", "12209")]


def test_booleano_e_data(banco_refined):
    produto = consultar(banco_refined, "SELECT descontinuado FROM refined.produtos WHERE produto_id = 20")
    admissao = consultar(banco_refined, "SELECT data_admissao FROM refined.vendedores WHERE vendedor_id = 1")
    assert produto == [(True,)]
    assert admissao == [(dt.date(2015, 3, 1),)]


def test_idempotente(banco_refined):
    assert executar_transformacao(banco_refined) == executar_transformacao(banco_refined)


def test_chave_duplicada_desfaz_tudo(pasta_raw, caminho_banco, tmp_path):
    executar_ingestao(pasta_raw, caminho_banco)
    pasta_sql = tmp_path / "sql"
    pasta_sql.mkdir()
    (pasta_sql / "transportadoras.sql").write_text(
        "SELECT 1 AS transportadora_id, 'x' AS transportadora", encoding="utf-8"
    )
    (pasta_sql / "duplicada.sql").write_text("SELECT 1 AS id UNION ALL SELECT 1", encoding="utf-8")

    with pytest.raises(ChaveDuplicadaError, match="refined.duplicada"):
        executar_transformacao(
            caminho_banco, pasta_sql, {"transportadoras": ["transportadora_id"], "duplicada": ["id"]}
        )
    assert consultar(caminho_banco, "SELECT count(*) FROM duckdb_tables() WHERE schema_name = 'refined'") == [(0,)]


def test_sql_ausente(caminho_banco, tmp_path):
    with pytest.raises(FileNotFoundError, match="pedidos"):
        executar_transformacao(caminho_banco, tmp_path, {"pedidos": ["pedido_id"]})
