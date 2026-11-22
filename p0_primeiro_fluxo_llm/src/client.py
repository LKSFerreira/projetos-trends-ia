"""Camada de comunicacao HTTP REST com a API da LLM."""

import os
import warnings
from pathlib import Path
from urllib.parse import urlsplit
from dotenv import load_dotenv
import requests
from urllib3.exceptions import InsecureRequestWarning
from src.contexto_prompt import preparar_solicitacao

# Carrega as variaveis do .env a partir da raiz do p0_primeiro_fluxo_llm
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", interpolate=False)


def ler_configuracao_booleana(nome: str, padrao: bool) -> bool:
    """Lê uma configuração que aceita os valores true ou false."""
    valor = os.getenv(nome, str(padrao)).strip().lower()

    if valor == "true":
        return True
    if valor == "false":
        return False

    raise ValueError(f"A variável {nome} deve conter true ou false.")


def ler_timeout_segundos(nome: str = "LLM_TIMEOUT_SECONDS", padrao: int = 30) -> int:
    """Lê o tempo limite em segundos e garante um inteiro positivo."""
    valor_bruto = os.getenv(nome, str(padrao)).strip()
    try:
        timeout = int(valor_bruto)
    except ValueError as erro:
        raise ValueError(f"A variável {nome} deve ser um número inteiro positivo.") from erro

    if timeout <= 0:
        raise ValueError(f"A variável {nome} deve ser um número inteiro positivo.")

    return timeout


def envia_prompt_llm(prompt: str) -> str:
    """Dispara a requisicao HTTP para a LLM com tratamento resiliente de erros.

    Args:
        prompt: Texto de entrada fornecido pelo usuario.

    Returns:
        str: Texto da resposta processada ou mensagem de erro amigavel.
    """
    api_host = os.getenv("HOST_API_LLM_INTERNO", "").strip()
    api_url = os.getenv("LLM_API_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "qwen3.5:9b-q4_K_M").strip()

    if not api_host:
        return "Erro de configuracao: A variável HOST_API_LLM_INTERNO não foi definida no .env"

    if not api_url:
        return "Erro de configuracao: A variável LLM_API_URL não foi definida no .env"

    url_analisada = urlsplit(api_url)
    if url_analisada.scheme not in {"http", "https"} or not url_analisada.netloc:
        return "Erro de configuração: A variável LLM_API_URL deve ser uma URL HTTP ou HTTPS válida."

    if not model:
        return "Erro de configuração: A variável LLM_MODEL não pode estar vazia."

    try:
        timeout = ler_timeout_segundos()
        verificar_tls = ler_configuracao_booleana("LLM_VERIFICAR_TLS", True)
        think = ler_configuracao_booleana("LLM_THINK", False)
    except ValueError as erro:
        return f"Erro de configuração: {erro}"

    headers = {
        "Content-Type": "application/json",
        "Host": api_host,
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    solicitacao = preparar_solicitacao(prompt, model, pensar=think)

    try:
        with warnings.catch_warnings():
            if not verificar_tls:
                warnings.filterwarnings("ignore", category=InsecureRequestWarning)
            response = requests.post(
                api_url,
                json=solicitacao,
                headers=headers,
                timeout=timeout,
                verify=verificar_tls,
            )

        if response.status_code == 401:
            return "Erro de autenticacao (401): A chave de API fornecida e invalida ou expirou."

        if response.status_code == 404:
            return "Erro (404): Endpoint ou modelo nao encontrado no servidor remoto."

        response.raise_for_status()
        dados = response.json()

        # Adaptacao para retornos padrao Ollama / OpenAI
        if "response" in dados:
            return str(dados["response"]).strip()
        if "choices" in dados and len(dados["choices"]) > 0:
            return str(dados["choices"][0]["message"]["content"]).strip()

        return str(dados)

    except requests.exceptions.Timeout:
        return f"Erro de conexao: A API da LLM demorou mais de {timeout} segundos para responder (Timeout)."
    except requests.exceptions.ConnectionError:
        return "Erro de conexao: Nao foi possivel estabelecer conexao com o servidor da LLM."
    except requests.exceptions.RequestException as erro:
        return f"Erro inesperado na chamada da API: {erro}"

