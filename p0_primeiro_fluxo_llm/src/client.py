"""Camada de comunicacao HTTP REST com a API da LLM."""

import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# Carrega as variaveis do .env a partir da raiz do p0_primeiro_fluxo_llm
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def envia_prompt_llm(prompt: str) -> str:
    """Dispara a requisicao HTTP para a LLM com tratamento resiliente de erros.

    Args:
        prompt: Texto de entrada fornecido pelo usuario.

    Returns:
        str: Texto da resposta processada ou mensagem de erro amigavel.
    """
    api_url = os.getenv("LLM_API_URL", "").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    model = os.getenv("LLM_MODEL", "qwen3.5:9b-q4_K_M").strip()
    timeout = int(os.getenv("LLM_TIMEOUT_SECONDS", "15"))

    if not api_url:
        return "Erro de configuracao: A variavel LLM_API_URL nao foi definida no .env."

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=timeout,
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

