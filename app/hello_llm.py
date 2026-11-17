import warnings

import requests
from urllib3.exceptions import InsecureRequestWarning

with warnings.catch_warnings(), requests.Session() as sessao:
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    sessao.trust_env = False
    resposta = sessao.post(
        "https://127.0.0.1:19001/api/generate",
        headers={"Host": "llm.example.invalid"},
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
