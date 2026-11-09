"""Testes da camada raw (pipeline.ingestao)."""

from __future__ import annotations

import duckdb
import pytest

from pipeline.config import TABELAS
from pipeline.ingestao import executar_ingestao


def test_grava_todas_as_tabelas_sem_descartar_linhas(pasta_raw, caminho_banco):
    resultado = executar_ingestao(pasta_raw, caminho_banco)

    assert set(resultado) == set(TABELAS.values())
    assert resultado["pedidos"] == 3
    assert resultado["itens_pedido"] == 5  # a linha duplicada é mantida na raw


def test_todas_as_colunas_entram_como_texto(pasta_raw, caminho_banco):
    executar_ingestao(pasta_raw, caminho_banco)

    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        tipos = conexao.execute(
            "SELECT DISTINCT data_type FROM information_schema.columns WHERE table_schema = 'raw'"
        ).fetchall()
    assert tipos == [("VARCHAR",)]


def test_nomes_de_colunas_e_valores_preservados(pasta_raw, caminho_banco):
    executar_ingestao(pasta_raw, caminho_banco)

    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        colunas = [c[0] for c in conexao.execute("DESCRIBE raw.clientes").fetchall()]
        cep, fax = conexao.execute("SELECT postalCode, fax FROM raw.clientes WHERE customerID = 'AAA'").fetchone()
    assert colunas[:3] == ["customerID", "companyName", "contactName"]
    assert cep == "01310"  # zero à esquerda preservado
    assert fax == "NULL"  # o texto 'NULL' ainda não é tratado na raw


def test_idempotente_rodar_duas_vezes_nao_duplica(pasta_raw, caminho_banco):
    primeira = executar_ingestao(pasta_raw, caminho_banco)
    segunda = executar_ingestao(pasta_raw, caminho_banco)

    assert primeira == segunda


def test_arquivo_ausente_nao_grava_nada(pasta_raw, caminho_banco):
    (pasta_raw / "orders.csv").unlink()

    with pytest.raises(FileNotFoundError, match="orders.csv"):
        executar_ingestao(pasta_raw, caminho_banco)
    assert not caminho_banco.exists()


def test_falha_no_meio_desfaz_tudo(pasta_raw, caminho_banco):
    executar_ingestao(pasta_raw, caminho_banco)
    (pasta_raw / "shippers.csv").write_bytes(b"shipperID\n\xff\xfe\n")  # bytes inválidos em UTF-8
    (pasta_raw / "orders.csv").write_text(
        "orderID,customerID\n99,ZZZ\n", encoding="utf-8"
    )

    with pytest.raises(duckdb.Error):
        executar_ingestao(pasta_raw, caminho_banco)

    with duckdb.connect(str(caminho_banco), read_only=True) as conexao:
        assert conexao.execute("SELECT count(*) FROM raw.pedidos").fetchone()[0] == 3
