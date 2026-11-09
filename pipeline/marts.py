"""Camada MARTS: indicadores de negócio materializados como tabelas.

Spec resumida:
    - Lê somente de refined e escreve somente no schema marts.
    - Cada arquivo sql/marts/NN_nome.sql (NN = dois dígitos) vira marts.nome.
    - Os arquivos rodam em ordem numérica; nomes fora do padrão são recusados.
    - O SQL deve ser um único SELECT (sem ';' no meio).
    - Tudo ou nada: se um indicador falhar, nenhum é gravado.
    - Idempotente: CREATE OR REPLACE TABLE.

Uso:
    uv run python -m pipeline.marts
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path

from pipeline.config import CAMINHO_BANCO, PASTA_SQL_MARTS
from pipeline.db import conectar

logger = logging.getLogger(__name__)

PADRAO_ARQUIVO = re.compile(r"^(\d{2})_([a-z][a-z0-9_]*)\.sql$")


@dataclass(frozen=True)
class ArquivoMart:
    """Um indicador: ordem de execução, nome da tabela e o SQL."""

    ordem: int
    tabela: str
    consulta: str


def ler_arquivos_marts(pasta_sql: Path) -> list[ArquivoMart]:
    """Lê e valida os arquivos .sql da pasta de marts.

    Raises:
        FileNotFoundError: se a pasta não existir ou não tiver nenhum .sql.
        ValueError: se algum arquivo tiver nome fora do padrão, ordem repetida,
            conteúdo vazio ou mais de um comando.
    """
    if not pasta_sql.is_dir():
        raise FileNotFoundError(f"Pasta de marts não encontrada: {pasta_sql}")
    arquivos = sorted(pasta_sql.glob("*.sql"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo .sql em {pasta_sql}")

    marts: list[ArquivoMart] = []
    ordens: set[int] = set()
    for arquivo in arquivos:
        casamento = PADRAO_ARQUIVO.match(arquivo.name)
        if not casamento:
            raise ValueError(f"Nome inválido '{arquivo.name}': use NN_nome_em_minusculas.sql")
        ordem = int(casamento.group(1))
        if ordem in ordens:
            raise ValueError(f"Ordem {ordem:02d} repetida em '{arquivo.name}'")
        ordens.add(ordem)

        consulta = arquivo.read_text(encoding="utf-8").strip().rstrip(";").strip()
        if not consulta:
            raise ValueError(f"Arquivo vazio: {arquivo.name}")
        if ";" in consulta:
            raise ValueError(f"'{arquivo.name}' deve ter um único SELECT")
        marts.append(ArquivoMart(ordem=ordem, tabela=casamento.group(2), consulta=consulta))
    return sorted(marts, key=lambda m: m.ordem)


def executar_marts(caminho_banco: Path = CAMINHO_BANCO, pasta_sql: Path = PASTA_SQL_MARTS) -> dict[str, int]:
    """Materializa cada indicador como tabela marts.<nome>.

    Returns:
        Dicionário tabela -> quantidade de linhas gravadas.
    """
    marts = ler_arquivos_marts(pasta_sql)
    resultado: dict[str, int] = {}
    conexao = conectar(caminho_banco)
    try:
        conexao.execute("BEGIN TRANSACTION")
        for mart in marts:
            conexao.execute(f"CREATE OR REPLACE TABLE marts.{mart.tabela} AS {mart.consulta}")
            resultado[mart.tabela] = conexao.execute(f"SELECT count(*) FROM marts.{mart.tabela}").fetchone()[0]
        conexao.execute("COMMIT")
    except Exception:
        conexao.execute("ROLLBACK")
        logger.error("Falha ao gerar marts. Nada foi gravado.")
        raise
    finally:
        conexao.close()

    for tabela, linhas in resultado.items():
        logger.info("marts.%-26s %5d linhas", tabela, linhas)
    logger.info("%d marts gerados", len(resultado))
    return resultado


if __name__ == "__main__":
    executar_marts()
