"""Verifica a ordem de preparação do túnel e uso da aplicação."""

from collections.abc import Iterator
from contextlib import contextmanager, nullcontext
from unittest.mock import Mock

import pytest

from src import app, tunel_devel


def test_pede_pergunta_apos_preparar_o_tunel(monkeypatch: pytest.MonkeyPatch) -> None:
    """A pergunta e a solicitação ocorrem dentro da sessão do túnel."""
    eventos: list[str] = []
    entradas = iter(["  ", "Como consulto um pedido?", "Como vejo a fila?", " SAIR "])

    @contextmanager
    def preparar_tunel() -> Iterator[None]:
        eventos.append("túnel disponível")
        yield
        eventos.append("sessão encerrada")

    def ler_pergunta(mensagem: str) -> str:
        eventos.append("pergunta lida")
        return next(entradas)

    def enviar_pergunta(pergunta: str) -> str:
        eventos.append(pergunta)
        return "Use a opção Buscar pedido."

    monkeypatch.setattr(app, "preparar_tunel_devel", preparar_tunel)
    monkeypatch.setattr(app, "verificar_encaminhamento_devel", lambda: None)
    monkeypatch.setattr("builtins.input", ler_pergunta)
    monkeypatch.setattr(app, "envia_prompt_llm", enviar_pergunta)

    app.main()

    assert eventos == [
        "túnel disponível",
        "pergunta lida",
        "pergunta lida",
        "Como consulto um pedido?",
        "pergunta lida",
        "Como vejo a fila?",
        "pergunta lida",
        "sessão encerrada",
    ]


def test_falha_na_abertura_impede_a_pergunta(monkeypatch: pytest.MonkeyPatch) -> None:
    """Uma falha no túnel encerra a execução antes da entrada de texto."""
    preparar_tunel = Mock(side_effect=RuntimeError("O túnel do Devel não abriu."))
    ler_pergunta, enviar_pergunta = Mock(), Mock()
    monkeypatch.setattr(app, "preparar_tunel_devel", preparar_tunel)
    monkeypatch.setattr("builtins.input", ler_pergunta)
    monkeypatch.setattr(app, "envia_prompt_llm", enviar_pergunta)

    with pytest.raises(SystemExit, match="O túnel do Devel não abriu"):
        app.main()

    ler_pergunta.assert_not_called()
    enviar_pergunta.assert_not_called()


def test_queda_do_tunel_impede_envio(monkeypatch: pytest.MonkeyPatch) -> None:
    enviar_pergunta = Mock()
    portas = iter([True, False])
    monkeypatch.setattr(app, "preparar_tunel_devel", nullcontext)
    monkeypatch.setattr("builtins.input", Mock(return_value="Como vejo a fila?"))
    monkeypatch.setattr(app, "envia_prompt_llm", enviar_pergunta)
    monkeypatch.setenv("LLM_API_URL", "https://127.0.0.1:19001/api/generate")
    monkeypatch.setattr(tunel_devel, "porta_local_aberta", lambda: next(portas))

    with pytest.raises(SystemExit, match="O túnel do Devel caiu"):
        app.main()

    enviar_pergunta.assert_not_called()


def test_preserva_codigo_da_falha_do_script(monkeypatch: pytest.MonkeyPatch) -> None:
    """O P0 encerra com o código do script, que já apresenta o diagnóstico."""
    processo = Mock()
    processo.poll.return_value = 1
    monkeypatch.setenv("LLM_API_URL", "https://127.0.0.1:19001/api/generate")
    monkeypatch.setattr(tunel_devel, "porta_local_aberta", lambda: False)
    monkeypatch.setattr(tunel_devel.subprocess, "Popen", Mock(return_value=processo))

    with pytest.raises(SystemExit) as saida:
        with tunel_devel.preparar_tunel_devel():
            pytest.fail("O encaminhamento falhou antes de ficar disponível.")

    assert saida.value.code == 1
