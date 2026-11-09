"""Camada REFINED: dados limpos, tipados e sem duplicatas (sem agregação).

Spec resumida:
    - Lê somente do schema raw e escreve somente no schema refined.
    - Cada arquivo sql/refined/<tabela>.sql é um SELECT que vira refined.<tabela>.
    - Os textos 'NULL' e vazios do CSV viram NULL de verdade (macro limpar()).
    - Tipos corretos (inteiro, decimal, data, booleano) e nomes em snake_case.
    - Validação de grão: para cada tabela, linhas == chaves primárias distintas.
      Se alguma falhar, nada é gravado (transação desfeita).
    - Idempotente: CREATE OR REPLACE.

Uso:
    uv run python -m pipeline.transformacao
"""

from __future__ import annotations

import logging
from pathlib import Path

import duckdb

from pipeline.config import CAMINHO_BANCO, CHAVES_PRIMARIAS, PASTA_SQL_REFINED
from pipeline.db import conectar

logger = logging.getLogger(__name__)

MACRO_LIMPAR = "CREATE OR REPLACE TEMP MACRO limpar(x) AS NULLIF(NULLIF(trim(x), 'NULL'), '')"


class ChaveDuplicadaError(Exception):
    """A tabela refined tem mais linhas do que chaves primárias distintas."""


def validar_chave_primaria(conexao: duckdb.DuckDBPyConnection, tabela: str, chave: list[str]) -> None:
    """Confere o grão da tabela: nenhuma combinação de chave pode se repetir nem ser nula.

    Raises:
        ChaveDuplicadaError: se houver repetição ou chave nula.
    """
    colunas = ", ".join(chave)
    nao_nulas = " AND ".join(f"{c} IS NOT NULL" for c in chave)
    linhas, distintas, validas = conexao.execute(
        f"""
        SELECT count(*),
               count(DISTINCT ({colunas})),
               count(*) FILTER (WHERE {nao_nulas})
        FROM refined.{tabela}
        """
    ).fetchone()
    if linhas != distintas or linhas != validas:
        raise ChaveDuplicadaError(
            f"refined.{tabela}: {linhas} linhas, {distintas} chaves distintas, "
            f"{linhas - validas} chaves nulas para ({colunas})"
        )


def executar_transformacao(
    caminho_banco: Path = CAMINHO_BANCO,
    pasta_sql: Path = PASTA_SQL_REFINED,
    chaves: dict[str, list[str]] = CHAVES_PRIMARIAS,
) -> dict[str, int]:
    """Materializa todas as tabelas refined a partir dos SQLs da pasta.

    Returns:
        Dicionário tabela -> quantidade de linhas gravadas.

    Raises:
        FileNotFoundError: se faltar o SQL de alguma tabela configurada.
        ChaveDuplicadaError: se alguma tabela violar a chave primária.
    """
    ausentes = [t for t in chaves if not (pasta_sql / f"{t}.sql").is_file()]
    if ausentes:
        raise FileNotFoundError(f"SQL ausente em {pasta_sql}: {', '.join(ausentes)}. Nada foi gravado.")

    resultado: dict[str, int] = {}
    conexao = conectar(caminho_banco)
    try:
        conexao.execute(MACRO_LIMPAR)
        conexao.execute("BEGIN TRANSACTION")
        for tabela, chave in chaves.items():
            consulta = (pasta_sql / f"{tabela}.sql").read_text(encoding="utf-8")
            conexao.execute(f"CREATE OR REPLACE TABLE refined.{tabela} AS {consulta}")
            validar_chave_primaria(conexao, tabela, chave)
            resultado[tabela] = conexao.execute(f"SELECT count(*) FROM refined.{tabela}").fetchone()[0]
        conexao.execute("COMMIT")
    except Exception:
        conexao.execute("ROLLBACK")
        logger.error("Falha na transformação. Nada foi gravado.")
        raise
    finally:
        conexao.close()

    for tabela, linhas in resultado.items():
        logger.info("refined.%-16s %6d linhas", tabela, linhas)
    return resultado


if __name__ == "__main__":
    executar_transformacao()
