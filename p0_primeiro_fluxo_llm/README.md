# P0: Primeiro Fluxo com Modelo de Linguagem (LLM)

Aplicação modular em Python que integra um modelo de linguagem de grande escala (LLM) por meio de uma interface de programação (API REST), resolvendo uma tarefa textual com resiliência a falhas, proteção rigorosa de credenciais e validação offline via testes unitários.

## Problema e exemplo

Uma pessoa que utiliza o escopo administrativo do LK SiGER precisa identificar quais opções do menu atendem às suas necessidades a partir de uma dúvida escrita, pois o sistema reúne diversas funções de gerenciamento.

O LK SiGER é um sistema de gerenciamento de recursos em desenvolvimento. Seu contexto administrativo atende pessoas nos papéis de atendente, gerente e administrador da empresa. A aplicação do P0 receberá uma dúvida textual e apresentará uma orientação sobre opções de menu relacionadas à necessidade informada.

**Exemplo de entrada:**

> Quero consultar os detalhes de um pedido que está aguardando atendimento.

**Exemplo de saída esperada:**

- Se você possui o número do protocolo, acesse o `Menu Principal`, toque em `[🔎 Buscar pedido]`, digite o protocolo e envie ao sistema. Essa opção permite acessar pedidos em aberto, em análise ou encerrados.

- Se você não possui o protocolo, acesse o `Menu Principal` e toque em `[📋 Fila operacional]`. Pedidos em aberto ou em análise podem ser visualizados nessa fila. Digite o número que representa o pedido e envie ao sistema para acessar a tela `Detalhes do Pedido`.

O exemplo descreve o resultado esperado para o projeto. Ele ainda não comprova uma resposta produzida pela aplicação.

## Justificativa para usar um modelo de linguagem

As pessoas podem descrever a mesma necessidade de maneiras diferentes. Por exemplo, uma pessoa que começou a usar o sistema há pouco tempo pode se referir ao protocolo como "código do pedido". Pessoas familiarizadas com o sistema também podem precisar de ajuda para encontrar funcionalidades que utilizam pouco.

Uma alternativa seria buscar palavras previamente cadastradas. Essa abordagem exigiria manter uma lista de expressões possíveis e poderia deixar de reconhecer uma dúvida formulada com palavras ausentes da lista. O modelo de linguagem foi escolhido para explorar sua capacidade de relacionar diferentes formulações às opções de menu fornecidas à aplicação.

O modelo pode interpretar uma dúvida incorretamente ou indicar uma opção inadequada. Suas respostas precisam ser avaliadas com exemplos, inclusive quando não houver uma opção apropriada entre as fornecidas. A justificativa apresenta uma expectativa para o projeto, não uma comprovação de desempenho superior à busca por palavras.

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

