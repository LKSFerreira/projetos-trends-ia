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


MENSAGENS_STATUS_HTTP = {
    401: "Erro de autenticação (401): A chave de API fornecida é inválida ou expirou.",
    403: "Erro de permissão (403): Acesso negado pelo servidor da LLM.",
    404: "Erro (404): Endpoint ou modelo não encontrado no servidor remoto.",
    429: "Erro (429): Limite de requisições atingido. Tente novamente em instantes.",
    500: "Serviço indisponível (500): O servidor da LLM encontrou uma falha interna.",
    502: "Serviço indisponível (502): Falha de comunicação entre o túnel e o servidor da LLM.",
    503: "Serviço indisponível (503): O servidor da LLM está temporariamente fora do ar ou em manutenção.",
    504: "Serviço indisponível (504): O servidor intermediário não recebeu resposta a tempo.",
}


def extrair_texto_resposta(response: requests.Response) -> str:
    """Valida o JSON retornado pelo servidor e extrai o texto útil da resposta."""
    try:
        dados = response.json()
    except ValueError:
        return "Erro de formato: O servidor retornou uma resposta que não está em JSON válido."

    if not isinstance(dados, dict):
        return "Erro de formato: A resposta do servidor veio em uma estrutura inesperada."

    texto = ""
    if "response" in dados:
        texto = str(dados["response"]).strip()
    elif "choices" in dados and isinstance(dados["choices"], list) and len(dados["choices"]) > 0:
        primeira_escolha = dados["choices"][0]
        if (
            isinstance(primeira_escolha, dict)
            and isinstance(primeira_escolha.get("message"), dict)
            and "content" in primeira_escolha["message"]
        ):
            texto = str(primeira_escolha["message"]["content"]).strip()
        else:
            return "Erro de formato: A resposta do servidor não trouxe o campo de conteúdo esperado."
    else:
        return "Erro de formato: A resposta do servidor não contém os campos esperados."

    if not texto:
        return "Erro de resposta: O modelo retornou uma resposta vazia."

    return texto


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

        if response.status_code in MENSAGENS_STATUS_HTTP:
            return MENSAGENS_STATUS_HTTP[response.status_code]

        if response.status_code >= 400:
            return f"Erro HTTP ({response.status_code}): O servidor recusou a solicitação."

        return extrair_texto_resposta(response)

    except requests.exceptions.Timeout:
        return f"Erro de conexao: A API da LLM demorou mais de {timeout} segundos para responder (Timeout)."
    except requests.exceptions.ConnectionError:
        return "Erro de conexao: Nao foi possivel estabelecer conexao com o servidor da LLM."
    except requests.exceptions.RequestException:
        return "Erro de comunicação: Não foi possível concluir a chamada para o servidor da LLM."

