# P0: Primeiro Fluxo com Modelo de Linguagem (LLM)

Aplicação modular em Python que integra um modelo de linguagem de grande escala por meio de uma interface de programação (API REST), resolvendo uma tarefa textual com resiliência a falhas, proteção rigorosa de credenciais e validação offline via testes unitários.

---

## Arquitetura do Projeto

```text
p0_primeiro_fluxo_llm/
├── src/
│   ├── app.py           # Interface de entrada (CLI), interação e formatação de saída
│   └── client.py        # Camada de comunicação HTTP/REST com a LLM (requests)
├── tests/
│   └── test_client.py   # Testes unitários offline com mocks (pytest)
├── .env.example         # Template público com nomes de variáveis de ambiente
├── requirements.txt     # Dependências externas com versões travadas (==)
└── README.md            # Instruções de instalação, execução e testes
```

---

## Quickstart / Como Executar

### 1. Clonar o repositório e entrar na pasta do P0
```bash
git clone https://github.com/LKSFerreira/projetos-trends-ia.git
cd projetos-trends-ia/p0_primeiro_fluxo_llm
```

### 2. Criar e ativar o ambiente virtual

**No Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**No Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env preenchendo as configurações da API
```

### 5. Executar a aplicação (CLI)
```bash
python -m src.app
```

### 6. Executar os testes unitários (100% offline)
```bash
pytest
```

---

## Marcos de Entrega (Tags Git)

A evolução do projeto segue os três checkpoints obrigatórios:

* `P0-basico`: Estrutura mínima funcional (chamada básica ao LLM funcionando).
* `P0-intermediario`: Tratamento de exceções (HTTP 401 e Timeout) com mensagens amigáveis no terminal.
* `P0-avancado`: Cobertura completa de testes unitários offline com `pytest` e `monkeypatch`.

