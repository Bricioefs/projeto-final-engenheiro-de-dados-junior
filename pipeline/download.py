"""Baixa os CSVs públicos da base Northwind para data/raw.

Os dados não são versionados no Git (data/ está no .gitignore); este script
é a forma reproduzível de obtê-los.

Uso:
    uv run python -m pipeline.download            # baixa só o que falta
    uv run python -m pipeline.download --forcar   # baixa tudo de novo
"""

from __future__ import annotations

import argparse
import logging
import urllib.request
from pathlib import Path

from pipeline.config import PASTA_RAW, TABELAS, URL_BASE_DADOS

logger = logging.getLogger(__name__)


def baixar_arquivos(
    pasta_destino: Path = PASTA_RAW,
    url_base: str = URL_BASE_DADOS,
    arquivos: list[str] | None = None,
    forcar: bool = False,
    timeout: int = 30,
) -> list[Path]:
    """Baixa cada CSV da fonte para a pasta de destino.

    Idempotente: arquivos que já existem são mantidos, a menos que forcar=True.
    O download vai para um arquivo temporário e só é renomeado no fim, para
    nunca deixar um CSV pela metade na pasta raw.

    Returns:
        Lista dos caminhos baixados nesta execução.

    Raises:
        RuntimeError: se algum download falhar (os já baixados são mantidos).
    """
    pasta_destino.mkdir(parents=True, exist_ok=True)
    baixados: list[Path] = []
    for nome in arquivos or list(TABELAS):
        destino = pasta_destino / nome
        if destino.exists() and not forcar:
            logger.info("%s já existe, mantido", nome)
            continue
        temporario = destino.with_suffix(".parcial")
        try:
            with urllib.request.urlopen(f"{url_base}/{nome}", timeout=timeout) as resposta:
                temporario.write_bytes(resposta.read())
        except Exception as erro:  # noqa: BLE001 - qualquer falha de rede vira erro claro
            temporario.unlink(missing_ok=True)
            raise RuntimeError(f"Falha ao baixar {nome}: {erro}") from erro
        temporario.replace(destino)
        logger.info("%s baixado (%d bytes)", nome, destino.stat().st_size)
        baixados.append(destino)
    return baixados


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa os CSVs da base Northwind")
    parser.add_argument("--forcar", action="store_true", help="baixa novamente mesmo se já existir")
    args = parser.parse_args()
    baixar_arquivos(forcar=args.forcar)


if __name__ == "__main__":
    main()
