"""Testes unitarios offline para o client HTTP com mocks (pytest)."""

import pytest
import requests
from src.client import envia_prompt_llm


class MockResponse:
    """Simula o objeto de resposta da biblioteca requests."""

    def __init__(self, json_data: dict, status_code: int = 200) -> None:
        self._json_data = json_data
        self.status_code = status_code

    def json(self) -> dict:
        return self._json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP Error {self.status_code}")


def test_envia_prompt_sucesso_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida o retorno bem-sucedido no formato de resposta do Ollama."""
    monkeypatch.setenv("LLM_API_URL", "https://llm-teste.fake/api/generate")
    monkeypatch.setenv("LLM_API_KEY", "fake_key")

    def mock_post(*args, **kwargs) -> MockResponse:
        return MockResponse({"response": "Ola! Sou uma resposta simulada."}, 200)

    monkeypatch.setattr(requests, "post", mock_post)

    resposta = envia_prompt_llm("Teste de prompt")
    assert resposta == "Ola! Sou uma resposta simulada."


def test_envia_prompt_erro_401(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida o tratamento amigavel para falha de autenticacao HTTP 401."""
    monkeypatch.setenv("LLM_API_URL", "https://llm-teste.fake/api/generate")

    def mock_post(*args, **kwargs) -> MockResponse:
        return MockResponse({}, 401)

    monkeypatch.setattr(requests, "post", mock_post)

    resposta = envia_prompt_llm("Teste com chave invalida")
    assert "Erro de autenticacao (401)" in resposta


def test_envia_prompt_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida a interceptacao amigavel de Timeout."""
    monkeypatch.setenv("LLM_API_URL", "https://llm-teste.fake/api/generate")

    def mock_post(*args, **kwargs) -> MockResponse:
        raise requests.exceptions.Timeout("Tempo limite esgotado")

    monkeypatch.setattr(requests, "post", mock_post)

    resposta = envia_prompt_llm("Teste de timeout")
    assert "Timeout" in resposta

