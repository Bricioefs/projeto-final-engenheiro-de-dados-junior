"""Teste do orquestrador: as etapas rodam na ordem certa e o download é opcional."""

from __future__ import annotations

import pipeline.__main__ as orquestrador


def test_ordem_das_etapas(monkeypatch):
    chamadas = []
    monkeypatch.setattr(orquestrador, "baixar_arquivos", lambda: chamadas.append("download"))
    monkeypatch.setattr(orquestrador, "executar_ingestao", lambda: chamadas.append("raw"))
    monkeypatch.setattr(orquestrador, "executar_transformacao", lambda: chamadas.append("refined"))
    monkeypatch.setattr(orquestrador, "executar_marts", lambda: chamadas.append("marts"))

    orquestrador.executar_pipeline()
    assert chamadas == ["raw", "refined", "marts"]

    chamadas.clear()
    orquestrador.executar_pipeline(baixar=True)
    assert chamadas == ["download", "raw", "refined", "marts"]
