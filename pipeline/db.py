"""Conexão com o banco DuckDB do projeto."""

from __future__ import annotations

from pathlib import Path

import duckdb

from pipeline.config import CAMINHO_BANCO

SCHEMAS = ("raw", "refined", "marts")


def conectar(caminho_banco: Path | str = CAMINHO_BANCO, somente_leitura: bool = False) -> duckdb.DuckDBPyConnection:
    """Abre uma conexão com o arquivo DuckDB e garante os schemas das três camadas.

    Args:
        caminho_banco: caminho do arquivo .duckdb. A pasta é criada se não existir.
        somente_leitura: abre sem permissão de escrita (usado pelo dashboard).

    Returns:
        Conexão DuckDB aberta. Quem chama é responsável por fechá-la.
    """
    caminho = Path(caminho_banco)
    if somente_leitura:
        return duckdb.connect(str(caminho), read_only=True)

    caminho.parent.mkdir(parents=True, exist_ok=True)
    conexao = duckdb.connect(str(caminho))
    for schema in SCHEMAS:
        conexao.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
    return conexao
