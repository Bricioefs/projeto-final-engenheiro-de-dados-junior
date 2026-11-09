"""Camada RAW: espelho fiel dos CSVs dentro do DuckDB.

Spec resumida:
    - Cada arquivo de config.TABELAS vira uma tabela raw.<nome>.
    - Todas as colunas entram como texto (VARCHAR): nenhuma conversão de tipo.
    - Nenhuma linha descartada e nenhum nome de coluna alterado.
    - Idempotente: CREATE OR REPLACE, rodar N vezes gera o mesmo resultado.
    - Se faltar algum arquivo, nada é gravado e o erro lista o que falta.
    - Tudo ou nada: as tabelas são gravadas em uma única transação.

Uso:
    uv run python -m pipeline.ingestao
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from pipeline.config import CAMINHO_BANCO, ENCODING_CSV, PASTA_RAW, TABELAS
from pipeline.db import conectar

logger = logging.getLogger(__name__)


def verificar_arquivos(pasta_raw: Path, tabelas: dict[str, str]) -> None:
    """Garante que todos os CSVs esperados existem antes de gravar qualquer coisa.

    Raises:
        FileNotFoundError: com a lista de arquivos ausentes.
    """
    ausentes = [nome for nome in tabelas if not (pasta_raw / nome).is_file()]
    if ausentes:
        raise FileNotFoundError(
            f"Arquivos ausentes em {pasta_raw}: {', '.join(ausentes)}. "
            "Rode 'uv run python -m pipeline.download'. Nada foi gravado."
        )


def gravar_tabela_raw(conexao: duckdb.DuckDBPyConnection, arquivo: Path, tabela: str) -> int:
    """Lê um CSV inteiro como texto e grava (substituindo) raw.<tabela>.

    Returns:
        Quantidade de linhas gravadas.
    """
    caminho_sql = str(arquivo).replace("'", "''")
    conexao.execute(
        f"""
        CREATE OR REPLACE TABLE raw.{tabela} AS
        SELECT *
        FROM read_csv(
            '{caminho_sql}',
            header = true,
            all_varchar = true,
            encoding = '{ENCODING_CSV}',
            delim = ',',
            quote = '"',
            escape = '"'
        )
        """
    )
    return conexao.execute(f"SELECT count(*) FROM raw.{tabela}").fetchone()[0]


def executar_ingestao(
    pasta_raw: Path = PASTA_RAW,
    caminho_banco: Path = CAMINHO_BANCO,
    tabelas: dict[str, str] = TABELAS,
) -> dict[str, int]:
    """Executa a ingestão de todos os arquivos para a camada raw.

    Returns:
        Dicionário tabela -> quantidade de linhas gravadas.
    """
    verificar_arquivos(pasta_raw, tabelas)
    resultado: dict[str, int] = {}
    conexao = conectar(caminho_banco)
    try:
        conexao.execute("BEGIN TRANSACTION")
        for arquivo, tabela in tabelas.items():
            resultado[tabela] = gravar_tabela_raw(conexao, pasta_raw / arquivo, tabela)
        conexao.execute("COMMIT")
    except Exception:
        conexao.execute("ROLLBACK")
        logger.error("Falha na ingestão. Nada foi gravado.")
        raise
    finally:
        conexao.close()

    for tabela, linhas in resultado.items():
        logger.info("raw.%-16s %6d linhas", tabela, linhas)
    return resultado


if __name__ == "__main__":
    executar_ingestao()
