"""Verifica a ordem de preparação do túnel e uso da aplicação."""

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import Mock

import pytest

from src import app


def test_pede_pergunta_apos_preparar_o_tunel(monkeypatch: pytest.MonkeyPatch) -> None:
    """A pergunta e a solicitação ocorrem dentro da sessão do túnel."""
    eventos: list[str] = []

    @contextmanager
    def preparar_tunel() -> Iterator[None]:
        eventos.append("túnel disponível")
        yield
        eventos.append("sessão encerrada")

    def ler_pergunta(mensagem: str) -> str:
        eventos.append("pergunta lida")
        return "Como consulto um pedido?"

    def enviar_pergunta(pergunta: str) -> str:
        eventos.append("pergunta enviada")
        return "Use a opção Buscar pedido."

    monkeypatch.setattr(app, "preparar_tunel_devel", preparar_tunel)
    monkeypatch.setattr("builtins.input", ler_pergunta)
    monkeypatch.setattr(app, "envia_prompt_llm", enviar_pergunta)

    app.main()

    assert eventos == [
        "túnel disponível", "pergunta lida", "pergunta enviada", "sessão encerrada"
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
