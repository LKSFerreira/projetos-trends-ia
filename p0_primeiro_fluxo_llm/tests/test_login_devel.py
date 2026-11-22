"""Verifica as recusas do login sem acessar o portal."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest
import requests


@pytest.fixture
def portal() -> ModuleType:
    """Carrega o script de infraestrutura sem executá-lo como programa."""
    raiz = Path(__file__).resolve().parents[2]
    caminho = raiz / "infra" / "tunel_devel" / "abrir_tunel_cloudflare.py"
    especificacao = spec_from_file_location("abrir_tunel_cloudflare", caminho)
    assert especificacao is not None and especificacao.loader is not None
    modulo = module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def resposta_simulada(codigo: int, html: str = "") -> requests.Response:
    """Cria uma resposta que aplica o tratamento real dos códigos HTTP."""
    resposta = requests.Response()
    resposta.status_code = codigo
    resposta.encoding = "utf-8"
    resposta._content = html.encode("utf-8")
    return resposta


@pytest.mark.parametrize("codigo", [200, 401, 403])
def test_recusa_permite_redigitar_campo_e_renova_token(
    codigo: int, portal: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    sessao = Mock(spec=requests.Session)
    sessao.get.side_effect = [
        resposta_simulada(200, '<input name="csrfmiddlewaretoken" value="primeiro">'),
        resposta_simulada(200, '<input name="csrfmiddlewaretoken" value="renovado">'),
    ]
    painel = '<a href="/logout/">Sair</a>'
    sessao.post.side_effect = [resposta_simulada(codigo), resposta_simulada(200, painel)]
    monkeypatch.setenv("DEVEL_EMAIL", "conta@example.test")
    monkeypatch.delenv("DEVEL_SENHA", raising=False)
    digitar_senha = Mock(side_effect=["primeira", "segunda"])
    monkeypatch.setattr(portal, "getpass", digitar_senha)

    assert portal.autenticar_no_portal(sessao) == painel
    assert digitar_senha.call_count == 2
    dados_enviados = [chamada.kwargs["data"] for chamada in sessao.post.call_args_list]
    assert [dados["csrfmiddlewaretoken"] for dados in dados_enviados] == ["primeiro", "renovado"]
    assert [dados["password"] for dados in dados_enviados] == ["primeira", "segunda"]


@pytest.mark.parametrize("codigo", [401, 403, 503])
def test_login_configurado_preserva_diagnostico_sem_repetir(
    codigo: int, portal: ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    sessao = Mock(spec=requests.Session)
    sessao.get.return_value = resposta_simulada(
        200, '<input name="csrfmiddlewaretoken" value="ficticio">'
    )
    sessao.post.return_value = resposta_simulada(codigo)
    monkeypatch.setenv("DEVEL_EMAIL", "conta@example.test")
    monkeypatch.setenv("DEVEL_SENHA", "senha-ficticia")

    if codigo == 503:
        with pytest.raises(requests.HTTPError) as falha:
            portal.autenticar_no_portal(sessao)
        assert falha.value.response is sessao.post.return_value
    else:
        with pytest.raises(RuntimeError, match=rf"HTTP {codigo}.*Revise DEVEL_EMAIL"):
            portal.autenticar_no_portal(sessao)

    sessao.post.assert_called_once()
