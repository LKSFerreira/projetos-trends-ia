# P0: Primeiro Fluxo com Modelo de Linguagem (LLM)

Aplicação em Python que utiliza um modelo de linguagem por meio de uma API para orientar dúvidas sobre opções do menu administrativo do LK SiGER.

## Problema e exemplo

Uma pessoa que utiliza o escopo administrativo do LK SiGER precisa identificar quais opções do menu atendem às suas necessidades a partir de uma dúvida escrita, pois o sistema reúne diversas funções de gerenciamento.

O LK SiGER é um sistema de gerenciamento de recursos em desenvolvimento. Seu contexto administrativo atende pessoas nos papéis de atendente, gerente e administrador da empresa. A aplicação do P0 receberá uma dúvida textual e apresentará uma orientação sobre opções de menu relacionadas à necessidade informada.

## Escopo do P0

A aplicação será executada pelo terminal, enviará a dúvida e as descrições das opções de menu a um modelo de linguagem e apresentará uma orientação em texto. Ela será independente do LK SiGER: não acessará pedidos reais nem executará funções no sistema.

**Exemplo de entrada:**

> Quero consultar os detalhes de um pedido que está aguardando atendimento.

**Exemplo de saída esperada:**

- Se você possui o número do protocolo, acesse o `Menu Principal`, toque em `[🔎 Buscar pedido]`, digite o protocolo e envie ao sistema. Essa opção permite acessar pedidos em aberto, em análise ou encerrados.

- Se você não possui o protocolo, acesse o `Menu Principal` e toque em `[📋 Fila operacional]`. Pedidos em aberto ou em análise podem ser visualizados nessa fila. Digite o número que representa o pedido e envie ao sistema para acessar a tela `Detalhes do Pedido`.

Esse exemplo descreve a saída esperada. As respostas observadas nos testes estão registradas mais adiante.

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
│   ├── client.py        # Comunicação HTTP/REST com a LLM (requests)
│   └── contexto_prompt.py # Contexto e opções fornecidas ao modelo
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

O exemplo está configurado para o modelo institucional Devel usando um encaminhamento SSH ativo para a porta local `19001`. O encaminhamento passa por um contêiner no ambiente Devel e por um túnel Cloudflare. A aplicação não inicia esse encaminhamento por conta própria. O Dockerfile e o script de descoberta estão em `infra/tunel_devel/`, na raiz do repositório.

`LLM_API_URL` indica a URL local encaminhada; `LLM_API_HOST` identifica o serviço interno; `LLM_MODEL` escolhe o modelo; `LLM_TIMEOUT_SECONDS` define o tempo limite. `LLM_THINK` controla o parâmetro `think` do modelo e `LLM_VERIFICAR_TLS` controla a verificação do certificado. A chave `LLM_API_KEY` pode ficar vazia no acesso institucional testado.

No laboratório, o certificado apresentado não correspondeu ao nome do serviço. Por isso, o exemplo define `LLM_VERIFICAR_TLS=false` para reproduzir o teste: nessa configuração, a identidade do serviço não é verificada pelo certificado. A solução definitiva para essa validação está pendente. Caso a variável não seja definida, o código mantém a verificação ativada.

### 5. Executar a aplicação (CLI)
```bash
python -m src.app
```

### 6. Executar os testes unitários (100% offline)
```bash
pytest
```

## Testes reais realizados

Os exemplos abaixo foram executados no terminal com o modelo `qwen3.5:9b-q4_K_M`, por meio do encaminhamento SSH e com verificação TLS desativada. Os resultados são observações pontuais: novas respostas podem variar.

| Entrada | Resultado observado |
| --- | --- |
| Preciso encontrar um pedido aguardando atendimento e consultar seus detalhes. | A resposta apresentou Buscar pedido pelo protocolo e Fila operacional para pedidos em aberto ou em análise. |
| Como faço para cancelar um pedido? | A resposta informou que não encontrou uma opção adequada nas informações fornecidas e não inventou um caminho de cancelamento. |

A aplicação não consulta pedidos nem executa operações no LK SiGER. A reprodução em ambiente limpo ainda não foi validada.

---

## Marcos de Entrega (Tags Git)

A evolução do projeto segue os três checkpoints obrigatórios:

* `p0-basico`: Primeiro fluxo funcional com entrada textual e resposta do LLM.
* `p0-intermediario`: Organização do fluxo e tratamento de erros.
* `p0-avancado`: Configuração, testes e entrega reproduzível.

