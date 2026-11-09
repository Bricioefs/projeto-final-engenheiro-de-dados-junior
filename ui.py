"""Abre a interface web do DuckDB (localhost) para explorar o banco com SQL.

Uso:
    uv run python ui.py

Feche com Ctrl+C. Enquanto a UI estiver aberta, o banco fica em uso:
feche-a antes de rodar o pipeline novamente.
"""

import time

import duckdb

from pipeline.config import CAMINHO_BANCO

if __name__ == "__main__":
    conexao = duckdb.connect(str(CAMINHO_BANCO))
    conexao.execute("CALL start_ui()")
    print("DuckDB UI aberta em http://localhost:4213  (Ctrl+C para sair)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        conexao.close()
