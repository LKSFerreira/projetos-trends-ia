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
projetos-trends-ia/
├── infra/
│   └── tunel_devel/
│       ├── abrir_tunel_cloudflare.py # Localiza o túnel e abre o encaminhamento SSH
│       └── docker/
│           ├── .dockerignore         # Restringe os arquivos enviados ao build
│           └── Dockerfile            # Define a imagem com SSH e cloudflared
└── p0_primeiro_fluxo_llm/
    ├── src/
    │   ├── app.py                    # Recebe a dúvida e exibe a resposta no terminal
    │   ├── client.py                 # Envia a requisição HTTP ao LLM
    │   ├── contexto_prompt.py        # Contexto e opções fornecidas ao modelo
    │   └── tunel_devel.py            # Reutiliza o túnel ou chama o script de abertura
    ├── tests/
    │   └── test_client.py            # Testes unitários do cliente com pytest
    ├── .env.example                  # Configuração de exemplo para o acesso institucional
    ├── exec_app.py                   # Prepara a configuração e inicia o P0
    ├── requirements.txt              # Dependências com versões fixadas
    └── README.md                     # Instruções de instalação, execução e testes
```

---

## Quickstart / Como Executar

O nível Básico requer uma conta com acesso ao modelo institucional Devel. Para quem está fora da capacitação, o suporte a um provedor externo com chave de API está planejado para o Intermediário.

### Execução rápida em um terminal

Com o contêiner em execução no Devel, a chave SSH preparada e `ssh` e `cloudflared` disponíveis, execute na pasta `p0_primeiro_fluxo_llm`.

**Com Python**

```bash
python exec_app.py
```

Se as dependências estiverem ausentes, o script prepara a pasta `.venv` e instala os pacotes nela. Se seu sistema disponibilizar Python como `python3`, execute `python3 exec_app.py`.

**Com uv**

```bash
uv run --no-project --with-requirements requirements.txt python exec_app.py
```

Nos dois caminhos, o script cria o `.env` se necessário e pede o host institucional se ele ainda não estiver configurado. O P0 verifica a porta local e abre o túnel se precisar. Informe o login do Devel e a frase de segurança da chave se forem solicitados. Digite a pergunta quando o campo de entrada aparecer.

### Execução passo a passo

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
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

No mesmo terminal, com a `.venv` ativa, instale as dependências com o Python desse ambiente.

```bash
python -m pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```bash
cp .env.example .env
```

Depois de copiar o exemplo, preencha `HOST_API_LLM_INTERNO` no `.env` com o nome do host informado pelo Devel. Use apenas o nome, sem `https://` e sem a porta. Os demais valores do exemplo já estão definidos para o acesso institucional.

- `LLM_API_URL` indica a URL local encaminhada.
- `HOST_API_LLM_INTERNO` identifica o serviço interno para a aplicação e para o encaminhamento SSH.
- `LLM_MODEL` seleciona o modelo.
- `LLM_TIMEOUT_SECONDS` define o tempo limite em segundos.
- `LLM_THINK` controla o parâmetro `think` do modelo.
- `LLM_VERIFICAR_TLS` controla a verificação do certificado.

O acesso institucional testado dispensa chave de API.

### 5. Abrir o túnel antes de executar a aplicação

Prepare a chave SSH e inicie o contêiner no Devel conforme o [artigo sobre o acesso ao LLM institucional](https://ead.hardware.org.br/mod/forum/discuss.php?d=1323). Os comandos `ssh` e `cloudflared` precisam estar disponíveis no computador local.

Ao usar o Dockerfile deste repositório, informe no ambiente do contêiner a variável `HOST_API_LLM_INTERNO` com o mesmo valor do `.env` local. O servidor SSH usa esse nome para limitar o encaminhamento ao LLM na porta `9001`.

No primeiro terminal, dentro de `p0_primeiro_fluxo_llm` e com o ambiente virtual ativo, execute o script incluído no repositório.

```bash
python ../infra/tunel_devel/abrir_tunel_cloudflare.py
```

Informe seu e-mail e sua senha do portal. Se o SSH pedir a frase de segurança da chave, informe-a também. Mantenha esse terminal aberto enquanto usa a aplicação. Ao terminar, pressione `Ctrl+C` nesse terminal para fechar o túnel.

### 6. Executar a aplicação (CLI)

Em um segundo terminal, entre em `p0_primeiro_fluxo_llm` e ative a `.venv` criado usando o comando do [passo 2](#2-criar-e-ativar-o-ambiente-virtual). Depois, execute a aplicação no mesmo terminal.

```bash
python -m src.app
```

Se aparecer `No module named 'dotenv'`, confira se você ativou a `.venv` nesse mesmo terminal e instalou as dependências conforme o passo 3. O pacote `python-dotenv` é instalado na `.venv` e importado como `dotenv`.

Antes de pedir a dúvida, o P0 verifica a porta local `19001` para reutilizar o encaminhamento. Se a porta estiver fechada, o P0 tenta abrir o túnel no próprio terminal e encerra essa conexão ao sair.

### 7. Executar os testes unitários (100% offline)

Na pasta `p0_primeiro_fluxo_llm`, com a `.venv` ativa, execute o pytest como módulo do Python. Assim, a pasta atual fica disponível para os testes importarem `src`.

```bash
python -m pytest
```

### 8. Tudo mastigado

Se preferir iniciar o P0 em um único terminal, use o script incluído no repositório. Com a chave SSH preparada e o contêiner em execução no Devel, rode o comando na pasta `p0_primeiro_fluxo_llm`.

```bash
python exec_app.py
```

## Erros conhecidos

### Permissão da chave SSH no Windows

Se o OpenSSH mostrar `UNPROTECTED PRIVATE KEY FILE` ou `bad permissions` ao carregar a chave, confira as permissões do arquivo. Ao copiar a chave para outro diretório, o Windows pode dar ao arquivo permissões herdadas da pasta, incluindo acesso de leitura para outros usuários ou grupos. O OpenSSH recusa usar a chave nesse caso. [Permissões de chaves no OpenSSH para Windows](https://github.com/PowerShell/Win32-OpenSSH/wiki/Security-protection-of-various-files-in-win32-openssh#user-private-key-files)

No PowerShell, dentro da pasta `p0_primeiro_fluxo_llm`, execute o bloco abaixo com a conta proprietária da chave. Ele ajusta apenas o arquivo privado `chave_tunel_devel`, sem a extensão `.pub`.

```powershell
$chave = '..\infra\tunel_devel\ssh_keys\chave_tunel_devel'
$conta = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
icacls.exe $chave /grant:r "${conta}:(F)"
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível conceder acesso à sua conta.' }
icacls.exe $chave /inheritance:r
```

O `icacls.exe` ajusta as permissões do arquivo. `/grant:r` garante primeiro uma permissão explícita de controle total `(F)` para sua conta. `/inheritance:r` desativa a herança e remove as permissões herdadas. [Referência do icacls](https://learn.microsoft.com/pt-br/windows-server/administration/windows-commands/icacls)

Depois, execute `python exec_app.py` novamente. Se o SSH pedir a frase de segurança, use a mesma da chave que você copiou.

### Erro HTTP 502 ao consultar o modelo

Um `502 Bad Gateway` pode indicar que o serviço do modelo no Devel está temporariamente indisponível ou que o intermediário não conseguiu obter uma resposta dele. No teste em clone limpo, duas tentativas retornaram 502 e uma tentativa posterior funcionou após o reinício do contêiner. A causa exata não foi confirmada.

1. No portal do Devel, pare o contêiner e aguarde alguns segundos.
2. Inicie o contêiner novamente e aguarde mais alguns segundos para o túnel ficar disponível.
3. Execute `python exec_app.py` e envie a pergunta novamente.

## Testes reais realizados

No teste manual em um clone limpo no Windows, `python exec_app.py` abriu o túnel e o modelo respondeu à pergunta sobre o que fazer com um protocolo em mãos. A resposta orientou a usar **Buscar pedido** para digitar o protocolo e consultar os detalhes.

Os exemplos abaixo foram executados no terminal com o modelo `qwen3.5:9b-q4_K_M`, por meio do encaminhamento SSH e com verificação TLS desativada. Os resultados são observações pontuais: novas respostas podem variar.

| Entrada | Resultado observado |
| --- | --- |
| Preciso encontrar um pedido aguardando atendimento e consultar seus detalhes. | A resposta apresentou Buscar pedido pelo protocolo e Fila operacional para pedidos em aberto ou em análise. |
| Como faço para cancelar um pedido? | A resposta informou que não encontrou uma opção adequada nas informações fornecidas e não inventou um caminho de cancelamento. |

A aplicação não consulta pedidos nem executa operações no LK SiGER.

---

## Marcos de Entrega (Tags Git)

A evolução do projeto segue os três checkpoints obrigatórios:

* `p0-basico`: Primeiro fluxo funcional com entrada textual e resposta do LLM.
* `p0-intermediario`: Organização do fluxo e tratamento de erros.
* `p0-avancado`: Configuração, testes e entrega reproduzível.

