"""Testes do download (sem acessar a internet: urlopen é substituído)."""

from __future__ import annotations

import io

import pytest

from pipeline import download


class RespostaFalsa(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_baixa_somente_o_que_falta(tmp_path, monkeypatch):
    (tmp_path / "a.csv").write_text("existente", encoding="utf-8")
    chamadas = []

    def urlopen_falso(url, timeout):
        chamadas.append(url)
        return RespostaFalsa(b"col\n1\n")

    monkeypatch.setattr(download.urllib.request, "urlopen", urlopen_falso)
    baixados = download.baixar_arquivos(tmp_path, "http://fonte", ["a.csv", "b.csv"])

    assert chamadas == ["http://fonte/b.csv"]
    assert baixados == [tmp_path / "b.csv"]
    assert (tmp_path / "a.csv").read_text(encoding="utf-8") == "existente"


def test_forcar_baixa_de_novo(tmp_path, monkeypatch):
    (tmp_path / "a.csv").write_text("antigo", encoding="utf-8")
    monkeypatch.setattr(download.urllib.request, "urlopen", lambda url, timeout: RespostaFalsa(b"novo"))

    download.baixar_arquivos(tmp_path, "http://fonte", ["a.csv"], forcar=True)

    assert (tmp_path / "a.csv").read_text(encoding="utf-8") == "novo"


def test_falha_de_rede_nao_deixa_arquivo_parcial(tmp_path, monkeypatch):
    def urlopen_quebrado(url, timeout):
        raise OSError("sem conexão")

    monkeypatch.setattr(download.urllib.request, "urlopen", urlopen_quebrado)

    with pytest.raises(RuntimeError, match="a.csv"):
        download.baixar_arquivos(tmp_path, "http://fonte", ["a.csv"])
    assert list(tmp_path.iterdir()) == []
