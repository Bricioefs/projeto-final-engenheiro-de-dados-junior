"""Orquestrador: roda o pipeline completo na ordem raw -> refined -> marts.

Uso:
    uv run python -m pipeline              # usa os CSVs que já estão em data/raw
    uv run python -m pipeline --baixar     # baixa os CSVs que faltarem antes
"""

from __future__ import annotations

import argparse
import logging
import time

from pipeline.download import baixar_arquivos
from pipeline.ingestao import executar_ingestao
from pipeline.marts import executar_marts
from pipeline.transformacao import executar_transformacao

logger = logging.getLogger("pipeline")


def executar_pipeline(baixar: bool = False) -> None:
    """Executa todas as etapas em sequência; para na primeira que falhar."""
    inicio = time.perf_counter()
    if baixar:
        baixar_arquivos()
    executar_ingestao()
    executar_transformacao()
    executar_marts()
    logger.info("Pipeline concluído em %.1fs", time.perf_counter() - inicio)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pipeline Northwind: raw -> refined -> marts")
    parser.add_argument("--baixar", action="store_true", help="baixa os CSVs que faltarem antes de rodar")
    executar_pipeline(baixar=parser.parse_args().baixar)


if __name__ == "__main__":
    main()
