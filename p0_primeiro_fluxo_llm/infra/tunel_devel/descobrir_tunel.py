"""Descobre o túnel do Devel e inicia o encaminhamento SSH local."""

import re
import subprocess
from getpass import getpass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

import requests

ENDERECO_PORTAL = "https://devel-llm.eastus.cloudapp.azure.com"
ENDERECO_LOGIN = f"{ENDERECO_PORTAL}/login/"
TEMPO_LIMITE = 15
CHAVE_SSH = Path(__file__).resolve().parent / "ssh_keys" / "chave_laboratorio"


class LeitorTokenLogin(HTMLParser):
    """Identifica o token de proteção no formulário de login."""

    def __init__(self) -> None:
        super().__init__()
        self.token: str | None = None

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        """Captura o valor do campo de proteção quando ele é encontrado."""
        atributos = dict(attrs)
        if tag == "input" and atributos.get("name") == "csrfmiddlewaretoken":
            self.token = atributos.get("value")


def autenticar_no_portal(sessao: requests.Session) -> str:
    """Autentica a sessão e devolve o HTML do painel."""
    resposta = sessao.get(ENDERECO_LOGIN, timeout=TEMPO_LIMITE)
    resposta.raise_for_status()

    leitor = LeitorTokenLogin()
    leitor.feed(resposta.text)
    if not leitor.token:
        raise RuntimeError("O token de proteção não foi encontrado no formulário.")

    print("Página de login recebida e token de proteção identificado.")
    email = input("E-mail do portal: ").strip()
    senha = getpass("Senha do portal: ")

    resposta = sessao.post(
        ENDERECO_LOGIN,
        data={
            "csrfmiddlewaretoken": leitor.token,
            "username": email,
            "password": senha,
            "next": "/",
        },
        headers={"Referer": ENDERECO_LOGIN},
        timeout=TEMPO_LIMITE,
    )
    resposta.raise_for_status()
    if "/logout/" not in resposta.text:
        raise RuntimeError("O login não foi confirmado. Confira os dados e tente novamente.")

    print("Login confirmado pelo painel do portal.")
    return resposta.text


def descobrir_endereco_tunel(sessao: requests.Session, painel: str) -> str:
    """Encontra nos logs o único endereço temporário do túnel."""
    caminhos_logs = set(re.findall(r'href=["\'](/container/\d+/logs/)["\']', painel))
    if len(caminhos_logs) != 1:
        raise RuntimeError(f"Esperado um link de logs; encontrados: {len(caminhos_logs)}.")

    caminho_logs = caminhos_logs.pop()
    print(f"Caminho dos logs encontrado: {caminho_logs}")
    resposta = sessao.get(f"{ENDERECO_PORTAL}{caminho_logs}", timeout=TEMPO_LIMITE)
    resposta.raise_for_status()

    enderecos_tunel = set(
        re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", resposta.text)
    )
    if len(enderecos_tunel) != 1:
        raise RuntimeError(
            f"Esperado um endereço de túnel; encontrados: {len(enderecos_tunel)}."
        )

    endereco_tunel = enderecos_tunel.pop()
    print(f"Endereço do túnel encontrado: {endereco_tunel}")
    return endereco_tunel


def iniciar_encaminhamento_ssh(endereco_tunel: str) -> None:
    """Mantém o encaminhamento SSH ativo até o processo ser encerrado."""
    nome_tunel = urlparse(endereco_tunel).hostname
    comando_ssh = [
        "ssh",
        "-i",
        str(CHAVE_SSH),
        "-o",
        "ProxyCommand=cloudflared access ssh --hostname %h",
        "-o",
        "ExitOnForwardFailure=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-L",
        "127.0.0.1:19001:llm.example.invalid:9001",
        "-N",
        f"laboratorio@{nome_tunel}",
    ]

    print("Iniciando o encaminhamento SSH. Use Ctrl+C para encerrar.")
    subprocess.run(comando_ssh, check=True)


def main() -> None:
    """Autentica no portal, descobre o túnel e inicia o SSH."""
    with requests.Session() as sessao:
        painel = autenticar_no_portal(sessao)
        endereco_tunel = descobrir_endereco_tunel(sessao, painel)

    iniciar_encaminhamento_ssh(endereco_tunel)


if __name__ == "__main__":
    main()
