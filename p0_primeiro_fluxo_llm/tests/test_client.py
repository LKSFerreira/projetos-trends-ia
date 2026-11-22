"""Testes unitarios offline para o client HTTP com mocks (pytest)."""

import pytest
import requests
from src.client import envia_prompt_llm
from src.contexto_prompt import CONTEXTO_LK_SIGER, preparar_solicitacao


@pytest.fixture(autouse=True)
def configurar_llm_de_teste(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isola os testes das variáveis de ambiente usadas pelo cliente."""
    monkeypatch.setenv("LLM_API_URL", "https://llm-teste.invalid/api/generate")
    monkeypatch.setenv("HOST_API_LLM_INTERNO", "llm-teste.invalid")
    monkeypatch.setenv("LLM_MODEL", "modelo-teste")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "30")
    monkeypatch.setenv("LLM_VERIFICAR_TLS", "true")
    monkeypatch.setenv("LLM_THINK", "false")
    monkeypatch.delenv("LLM_API_KEY", raising=False)


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


def test_prepara_solicitacao_com_contexto_e_pergunta() -> None:
    """Confere o corpo completo sem chamar o serviço."""
    solicitacao = preparar_solicitacao("Como consulto um pedido?", "modelo-teste", pensar=True)

    assert solicitacao == {
        "model": "modelo-teste",
        "prompt": f"{CONTEXTO_LK_SIGER}\n\nDúvida do usuário: Como consulto um pedido?",
        "stream": False,
        "think": True,
    }


def test_envia_prompt_sucesso_ollama(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida o retorno bem-sucedido no formato de resposta do Ollama."""
    monkeypatch.setenv("LLM_API_KEY", "fake_key")

    def mock_post(*args, **kwargs) -> MockResponse:
        assert kwargs["json"] == preparar_solicitacao(
            "Teste de prompt", "modelo-teste", pensar=False
        )
        return MockResponse({"response": "Ola! Sou uma resposta simulada."}, 200)

    monkeypatch.setattr(requests, "post", mock_post)

    resposta = envia_prompt_llm("Teste de prompt")
    assert resposta == "Ola! Sou uma resposta simulada."


def test_envia_prompt_erro_401(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida o tratamento amigavel para falha de autenticacao HTTP 401."""
    def mock_post(*args, **kwargs) -> MockResponse:
        return MockResponse({}, 401)

    monkeypatch.setattr(requests, "post", mock_post)

    resposta = envia_prompt_llm("Teste com chave invalida")
    assert "Erro de autenticacao (401)" in resposta


def test_envia_prompt_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Valida a interceptacao amigavel de Timeout."""
    def mock_post(*args, **kwargs) -> MockResponse:
        raise requests.exceptions.Timeout("Tempo limite esgotado")

    monkeypatch.setattr(requests, "post", mock_post)

    resposta = envia_prompt_llm("Teste de timeout")
    assert "Timeout" in resposta


@pytest.mark.parametrize(
    ("variavel", "valor", "trecho_esperado"),
    [
        ("LLM_TIMEOUT_SECONDS", "abc", "LLM_TIMEOUT_SECONDS"),
        ("LLM_TIMEOUT_SECONDS", "0", "LLM_TIMEOUT_SECONDS"),
        ("LLM_VERIFICAR_TLS", "talvez", "LLM_VERIFICAR_TLS"),
        ("LLM_API_URL", "endereco-invalido", "LLM_API_URL"),
        ("LLM_MODEL", "", "LLM_MODEL"),
    ],
)
def test_envia_prompt_rejeita_configuracao_invalida_sem_rede(
    monkeypatch: pytest.MonkeyPatch,
    variavel: str,
    valor: str,
    trecho_esperado: str,
) -> None:
    """Garante que configuracoes invalidas falhem localmente antes de chamar a rede."""
    monkeypatch.setenv(variavel, valor)

    def nao_deve_chamar_rede(*args, **kwargs) -> MockResponse:
        raise AssertionError("Não deveria chamar requests.post com configuração inválida.")

    monkeypatch.setattr(requests, "post", nao_deve_chamar_rede)

    resposta = envia_prompt_llm("Teste de configuração")
    assert "Erro de configuração:" in resposta
    assert trecho_esperado in resposta

