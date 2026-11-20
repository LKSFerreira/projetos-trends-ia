"""Prepara a configuração local e inicia o P0 no terminal."""

import importlib
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

PASTA_P0 = Path(__file__).resolve().parent
ARQUIVO_ENV = PASTA_P0 / ".env"
EXEMPLO_ENV = PASTA_P0 / ".env.example"
VARIAVEL_HOST = "HOST_API_LLM_INTERNO"
PASTA_AMBIENTE = PASTA_P0 / ".venv"
REQUISITOS = PASTA_P0 / "requirements.txt"


def preparar_dependencias() -> None:
    """Usa o ambiente atual quando pronto ou prepara a pasta local ``.venv``."""
    if all(importlib.util.find_spec(nome) for nome in ("dotenv", "requests")):
        return

    try:
        if Path(sys.prefix).resolve() != PASTA_AMBIENTE.resolve():
            if os.name == "nt":
                python_local = PASTA_AMBIENTE / "Scripts" / "python.exe"
            else:
                python_local = PASTA_AMBIENTE / "bin" / "python"

            if not python_local.is_file():
                print("Criando o ambiente virtual do P0...", flush=True)
                subprocess.run(
                    [sys.executable, "-m", "venv", str(PASTA_AMBIENTE)], check=True
                )

            resultado = subprocess.run([str(python_local), str(Path(__file__).resolve())])
            raise SystemExit(resultado.returncode)

        print("Instalando as dependências do P0 no ambiente virtual...", flush=True)
        if importlib.util.find_spec("pip") is None:
            subprocess.run([sys.executable, "-m", "ensurepip"], check=True)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(REQUISITOS)], check=True
        )
        importlib.invalidate_caches()
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit(
            "\nNão foi possível preparar o ambiente virtual do P0."
        ) from None


def main() -> None:
    """Reutiliza a configuração existente ou solicita o host na primeira execução."""
    preparar_dependencias()
    from dotenv import dotenv_values, set_key

    if not ARQUIVO_ENV.exists():
        configuracao_padrao = EXEMPLO_ENV.read_bytes()
        try:
            with ARQUIVO_ENV.open("xb") as arquivo:
                arquivo.write(configuracao_padrao)
        except FileExistsError:
            pass

    host = (
        os.getenv(VARIAVEL_HOST) or dotenv_values(ARQUIVO_ENV).get(VARIAVEL_HOST) or ""
    ).strip()
    primeira_configuracao = not host
    if primeira_configuracao:
        host = input(
            "\nNome do host informado pelo Devel, sem protocolo ou porta.\n"
            "Exemplo: llm-teste.software\n> "
        ).strip()

    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9.-]*", host):
        raise SystemExit(
            f"Informe um nome de host válido em {VARIAVEL_HOST}, sem protocolo ou porta."
        )

    if primeira_configuracao:
        set_key(ARQUIVO_ENV, VARIAVEL_HOST, host, quote_mode="never")
    os.environ[VARIAVEL_HOST] = host

    from src.app import main as executar_aplicacao

    executar_aplicacao()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nExecução interrompida.")
        raise SystemExit(130) from None
