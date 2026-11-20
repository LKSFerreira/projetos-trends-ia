"""Gerencia o encaminhamento local usado pelo P0."""

import os
import socket
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit

ENDERECO_LOCAL = ("127.0.0.1", 19001)
SCRIPT_TUNEL = (
    Path(__file__).resolve().parents[2]
    / "infra" / "tunel_devel" / "abrir_tunel_cloudflare.py"
)


def usa_encaminhamento_devel() -> bool:
    """Identifica a entrada local do túnel na URL configurada."""
    try:
        destino = urlsplit(os.getenv("LLM_API_URL", "").strip())
        return destino.scheme == "https" and (destino.hostname, destino.port) == ENDERECO_LOCAL
    except ValueError:
        return False


def porta_local_aberta() -> bool:
    """Verifica se há um processo escutando na porta do encaminhamento."""
    try:
        with socket.create_connection(ENDERECO_LOCAL, timeout=0.5):
            return True
    except OSError:
        return False


def encerrar_tunel(processo: subprocess.Popen) -> None:
    """Encerra o script iniciado pela aplicação e sua conexão SSH."""
    if processo.poll() is not None:
        return

    if os.name == "nt":
        resultado = subprocess.run(
            ["taskkill", "/PID", str(processo.pid), "/T", "/F"],
            capture_output=True,
            check=False,
        )
        if resultado.returncode and processo.poll() is None:
            print("Não foi possível encerrar o túnel iniciado pelo P0.", file=sys.stderr)
            return
    else:
        processo.terminate()

    try:
        processo.wait(timeout=5)
    except subprocess.TimeoutExpired:
        processo.kill()
        processo.wait()


@contextmanager
def preparar_tunel_devel() -> Iterator[None]:
    """Reutiliza o túnel existente ou abre um para esta execução."""
    if not usa_encaminhamento_devel() or porta_local_aberta():
        yield
        return

    print("Abrindo o túnel do Devel. Siga as instruções de acesso no terminal.", flush=True)
    try:
        processo = subprocess.Popen([sys.executable, str(SCRIPT_TUNEL)])
    except OSError as erro:
        raise RuntimeError("Não foi possível executar abrir_tunel_cloudflare.py.") from erro

    try:
        while not porta_local_aberta():
            try:
                processo.wait(timeout=0.25)
            except subprocess.TimeoutExpired:
                continue
            raise RuntimeError("O túnel do Devel não abriu. Confira a mensagem acima.")
        if processo.poll() is not None:
            raise RuntimeError("O túnel do Devel encerrou durante a abertura.")
        yield
    finally:
        encerrar_tunel(processo)
