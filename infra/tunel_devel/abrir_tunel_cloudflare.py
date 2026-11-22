"""Descobre o túnel do Devel e inicia o encaminhamento SSH local."""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import signal
import subprocess
import sys
from getpass import getpass
from html.parser import HTMLParser
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlparse

ENDERECO_PORTAL = "https://devel-llm.eastus.cloudapp.azure.com"
ENDERECO_LOGIN = f"{ENDERECO_PORTAL}/login/"
TEMPO_LIMITE = 15
CHAVE_SSH = Path(__file__).resolve().parent / "ssh_keys" / "chave_tunel_devel"
ARQUIVO_ENV = Path(__file__).resolve().parents[2] / "p0_primeiro_fluxo_llm" / ".env"


class TunelNaoEncontrado(Exception):
    """Indica que os registros não contêm o endereço do túnel."""


def verificar_requisitos() -> list[str]:
    """Identifica requisitos locais ausentes antes de acessar o portal."""
    problemas = []
    if importlib.util.find_spec("requests") is None:
        problemas.append(
            "Biblioteca requests não encontrada. Instale-a no ambiente Python "
            "usado para executar o script. Consulte o README do P0."
        )
    if importlib.util.find_spec("dotenv") is None:
        problemas.append(
            "Biblioteca python-dotenv não encontrada. Instale as dependências "
            "do P0 conforme o README."
        )
    if shutil.which("ssh") is None:
        problemas.append(
            "Comando ssh não encontrado. Instale o cliente OpenSSH e confira o PATH."
        )
    if shutil.which("cloudflared") is None:
        problemas.append(
            "Comando cloudflared não encontrado. Instale o cloudflared no computador "
            "local e confira o PATH."
        )
    if not CHAVE_SSH.is_file():
        problemas.append(
            "Chave privada SSH não encontrada.\n"
            "  Coloque o arquivo da chave privada, sem a extensão .pub, neste caminho:\n"
            f"  {CHAVE_SSH}\n"
            "  Se ainda não gerou a chave, siga a etapa de preparação indicada no README."
        )
    return problemas


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
    print("\n" + "=" * 100)
    print("  ACESSO AO DEVEL LLM PORTAL")
    print("=" * 100 + "\n")
    email_configurado = os.getenv("DEVEL_EMAIL", "").strip()
    senha_configurada = os.getenv("DEVEL_SENHA", "")

    while True:
        resposta = sessao.get(ENDERECO_LOGIN, timeout=TEMPO_LIMITE)
        resposta.raise_for_status()

        leitor = LeitorTokenLogin()
        leitor.feed(resposta.text)
        if not leitor.token:
            raise RuntimeError("O token de proteção não foi encontrado no formulário.")

        email = email_configurado or input("E-mail do portal: ").strip()
        senha = senha_configurada or getpass("Senha do portal: ")
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
        recusa_http = resposta.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN)
        if not recusa_http:
            resposta.raise_for_status()
            if "/logout/" in resposta.text:
                print("\nLogin confirmado pelo painel do portal.")
                return resposta.text

        codigo_recusa = f" (HTTP {resposta.status_code})" if recusa_http else ""
        if email_configurado and senha_configurada:
            raise RuntimeError(
                f"Login recusado{codigo_recusa}. Revise DEVEL_EMAIL e DEVEL_SENHA no .env."
            )

        print(
            f"\nLogin não confirmado{codigo_recusa}. "
            "Digite os dados novamente ou pressione Ctrl+C.\n"
        )


def descobrir_endereco_tunel(sessao: requests.Session, painel: str) -> str:
    """Encontra nos logs o único endereço temporário do túnel."""
    caminhos_logs = set(re.findall(r'href=["\'](/container/\d+/logs/)["\']', painel))
    if len(caminhos_logs) != 1:
        raise RuntimeError(f"Esperado um link de logs; encontrados: {len(caminhos_logs)}.")

    caminho_logs = caminhos_logs.pop()
    resposta = sessao.get(f"{ENDERECO_PORTAL}{caminho_logs}", timeout=TEMPO_LIMITE)
    resposta.raise_for_status()

    enderecos_tunel = set(
        re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", resposta.text)
    )
    if not enderecos_tunel:
        raise TunelNaoEncontrado(
            "Nenhum endereço de túnel foi encontrado nos logs. "
            "Verifique se o container está em execução no portal. "
            "Se estiver, aguarde a criação do túnel e confira os logs antes de tentar novamente."
        )
    if len(enderecos_tunel) != 1:
        raise RuntimeError(
            f"Esperado um endereço de túnel; encontrados: {len(enderecos_tunel)}."
        )

    endereco_tunel = enderecos_tunel.pop()
    print(f"Endereço do túnel encontrado: {endereco_tunel}")
    return endereco_tunel


def iniciar_encaminhamento_ssh(endereco_tunel: str, host_llm: str) -> None:
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
        f"127.0.0.1:19001:{host_llm}:9001",
        "-N",
        f"tunel_devel@{nome_tunel}",
    ]

    print("\n" + "-" * 100)
    print("Iniciando o encaminhamento SSH. Use Ctrl+C para encerrar.")
    print("-" * 100 + "\n", flush=True)
    subprocess.run(comando_ssh, check=True)


def main() -> None:
    """Autentica no portal, descobre o túnel e inicia o SSH."""
    problemas = verificar_requisitos()
    if problemas:
        print("\nNão foi possível abrir o túnel do Devel.\n", file=sys.stderr)
        print("\n\n".join(f"- {problema}" for problema in problemas), file=sys.stderr)
        raise SystemExit(1)

    import requests
    from dotenv import load_dotenv

    load_dotenv(ARQUIVO_ENV, interpolate=False)
    host_llm = os.getenv("HOST_API_LLM_INTERNO", "")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]*", host_llm):
        raise SystemExit(
            "Preencha HOST_API_LLM_INTERNO em p0_primeiro_fluxo_llm/.env com o nome "
            "do host informado pelo Devel, sem protocolo ou porta."
        )

    try:
        with requests.Session() as sessao:
            painel = autenticar_no_portal(sessao)
            endereco_tunel = descobrir_endereco_tunel(sessao, painel)
    except requests.exceptions.Timeout:
        print("Erro: O portal demorou para responder. Confira sua conexão e tente novamente.", file=sys.stderr)
        raise SystemExit(1) from None
    except requests.exceptions.ConnectionError:
        print("Erro: Não foi possível conectar ao portal. Confira sua conexão e a disponibilidade do Devel.", file=sys.stderr)
        raise SystemExit(1) from None
    except requests.exceptions.HTTPError as erro:
        codigo = erro.response.status_code if erro.response is not None else "desconhecido"
        print(f"Erro: O portal respondeu com HTTP {codigo}. Confira o portal e tente novamente.", file=sys.stderr)
        raise SystemExit(1) from None
    except requests.exceptions.RequestException:
        print("Erro: A solicitação ao portal falhou. Confira sua conexão e tente novamente.", file=sys.stderr)
        raise SystemExit(1) from None
    except (TunelNaoEncontrado, RuntimeError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        raise SystemExit(1) from None

    try:
        iniciar_encaminhamento_ssh(endereco_tunel, host_llm)
    except subprocess.CalledProcessError as erro:
        print(f"\nO SSH encerrou com código {erro.returncode}.", file=sys.stderr)
        raise SystemExit(1) from None
    except FileNotFoundError:
        print("Erro: Não foi possível iniciar o SSH. Verifique se ele está disponível no PATH.", file=sys.stderr)
        raise SystemExit(1) from None


def encerrar_por_sinal(numero_sinal: int, quadro: object) -> None:
    """Interrompe a espera pelo SSH quando a aplicação encerra o script."""
    raise SystemExit(128 + numero_sinal)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, encerrar_por_sinal)
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.", file=sys.stderr)
        raise SystemExit(130) from None
