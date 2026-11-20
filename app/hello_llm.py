import os
import warnings
from pathlib import Path

import requests
from dotenv import load_dotenv
from urllib3.exceptions import InsecureRequestWarning

load_dotenv(Path(__file__).resolve().parents[1] / "p0_primeiro_fluxo_llm" / ".env")
host_llm_interno = os.getenv("HOST_API_LLM_INTERNO", "").strip()
if not host_llm_interno:
    raise SystemExit("Preencha HOST_API_LLM_INTERNO em p0_primeiro_fluxo_llm/.env.")

with warnings.catch_warnings(), requests.Session() as sessao:
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    sessao.trust_env = False
    resposta = sessao.post(
        "https://127.0.0.1:19001/api/generate",
        headers={"Host": host_llm_interno},
        json={
            "model": "qwen3.5:9b-q4_K_M",
            "prompt": "Responda com uma frase curta e inspiradora sobre transformar desafios em soluções.",
            "think": False,
            "stream": False,
        },
        timeout=120,
        verify=False,
    )
    resposta.raise_for_status()
    print("\n" + resposta.json()["response"])
