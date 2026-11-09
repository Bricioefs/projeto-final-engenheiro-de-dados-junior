"""Fixtures dos testes: dados inventados e banco temporário.

Nenhum teste usa os dados reais nem o banco do projeto (data/northwind.duckdb).
"""

from __future__ import annotations

from pathlib import Path

import pytest

# CSVs inventados, com os mesmos cabeçalhos da fonte Northwind.
# Cenários embutidos: 'NULL' como texto, pedido sem envio, entrega atrasada,
# desconto, CEP com zero à esquerda e uma linha de item duplicada.
CSVS_FALSOS: dict[str, str] = {
    "orders.csv": (
        "orderID,customerID,employeeID,orderDate,requiredDate,shippedDate,shipVia,freight,"
        "shipName,shipAddress,shipCity,shipRegion,shipPostalCode,shipCountry\n"
        "1,AAA,1,2020-01-10 00:00:00.000,2020-01-20 00:00:00.000,2020-01-15 00:00:00.000,1,10.50,"
        "Loja A,Rua 1,São Carlos,SP,01310,Brazil\n"
        "2,AAA,2,2020-01-25 00:00:00.000,2020-02-01 00:00:00.000,2020-02-05 00:00:00.000,2,20.00,"
        "Loja A,Rua 1,São Carlos,SP,01310,Brazil\n"
        "3,BBB,1,2020-02-03 00:00:00.000,2020-02-20 00:00:00.000,NULL,1,5.00,"
        "Shop B,Main St,Berlin,NULL,12209,Germany\n"
    ),
    "order_details.csv": (
        "orderID,productID,unitPrice,quantity,discount\n"
        "1,10,100.00,2,0\n"
        "1,20,50.00,1,0.1\n"
        "2,10,100.00,1,0\n"
        "3,20,50.00,4,0.25\n"
        "3,20,50.00,4,0.25\n"
    ),
    "products.csv": (
        "productID,productName,supplierID,categoryID,quantityPerUnit,unitPrice,unitsInStock,"
        "unitsOnOrder,reorderLevel,discontinued\n"
        "10,Café,1,1,1 kg,100.00,5,0,1,0\n"
        "20,Queijo,1,2,500 g,50.00,0,10,2,1\n"
    ),
    "categories.csv": (
        "categoryID,categoryName,description,picture\n"
        "1,Bebidas,Cafés e chás,0x00\n"
        "2,Laticínios,Queijos,0x00\n"
    ),
    "customers.csv": (
        "customerID,companyName,contactName,contactTitle,address,city,region,postalCode,country,phone,fax\n"
        "AAA,Empresa A,Ana,Dona,Rua 1,São Carlos,SP,01310,Brazil,1,NULL\n"
        "bbb,Firma B,Bob,Owner,Main St,Berlin,NULL,12209,Germany,2,NULL\n"
    ),
    "employees.csv": (
        "employeeID,lastName,firstName,title,titleOfCourtesy,birthDate,hireDate,address,city,"
        "region,postalCode,country,homePhone,extension,photo,notes,reportsTo,photoPath\n"
        "1,Silva,Maria,Vendedora,Ms.,1980-01-01 00:00:00.000,2015-03-01 00:00:00.000,Rua,SP,"
        "NULL,0,Brazil,0,1,0x00,nota,2,x\n"
        "2,Souza,João,Gerente,Mr.,1975-01-01 00:00:00.000,2010-03-01 00:00:00.000,Rua,SP,"
        "NULL,0,Brazil,0,2,0x00,nota,NULL,x\n"
    ),
    "suppliers.csv": (
        "supplierID,companyName,contactName,contactTitle,address,city,region,postalCode,country,"
        "phone,fax,homePage\n"
        "1,Fornecedor X,Zé,Dono,Rua,Campinas,SP,13000,Brazil,0,NULL,NULL\n"
    ),
    "shippers.csv": "shipperID,companyName,phone\n1,Transp Rápida,111\n2,Transp Lenta,222\n",
}


@pytest.fixture
def pasta_raw(tmp_path: Path) -> Path:
    """Pasta temporária com todos os CSVs inventados."""
    pasta = tmp_path / "raw"
    pasta.mkdir()
    for nome, conteudo in CSVS_FALSOS.items():
        (pasta / nome).write_text(conteudo, encoding="utf-8")
    return pasta


@pytest.fixture
def caminho_banco(tmp_path: Path) -> Path:
    """Caminho de um banco DuckDB temporário (ainda não criado)."""
    return tmp_path / "teste.duckdb"
