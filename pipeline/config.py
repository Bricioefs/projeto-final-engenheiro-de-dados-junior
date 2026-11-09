"""Configuração central do projeto: caminhos, fonte dos dados e mapa arquivo -> tabela.

Tudo que muda de ambiente para ambiente fica aqui, para que os módulos do pipeline
não tenham caminhos ou nomes "chumbados" no código.
"""

from __future__ import annotations

from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent

PASTA_RAW = RAIZ_PROJETO / "data" / "raw"
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "northwind.duckdb"
PASTA_SQL_REFINED = RAIZ_PROJETO / "sql" / "refined"
PASTA_SQL_MARTS = RAIZ_PROJETO / "sql" / "marts"

ENCODING_CSV = "utf-8"

# Fonte pública: base de exemplo Northwind (Microsoft), exportada em CSV.
URL_BASE_DADOS = (
    "https://raw.githubusercontent.com/graphql-compose/graphql-compose-examples/"
    "master/examples/northwind/data/csv"
)

# Arquivo CSV de origem -> nome da tabela nas camadas raw e refined.
TABELAS: dict[str, str] = {
    "orders.csv": "pedidos",
    "order_details.csv": "itens_pedido",
    "products.csv": "produtos",
    "categories.csv": "categorias",
    "customers.csv": "clientes",
    "employees.csv": "vendedores",
    "suppliers.csv": "fornecedores",
    "shippers.csv": "transportadoras",
}

# Chave primária (grão) de cada tabela da camada refined.
# Regra: número de linhas == número de chaves distintas.
CHAVES_PRIMARIAS: dict[str, list[str]] = {
    "pedidos": ["pedido_id"],
    "itens_pedido": ["pedido_id", "produto_id"],
    "produtos": ["produto_id"],
    "categorias": ["categoria_id"],
    "clientes": ["cliente_id"],
    "vendedores": ["vendedor_id"],
    "fornecedores": ["fornecedor_id"],
    "transportadoras": ["transportadora_id"],
}
