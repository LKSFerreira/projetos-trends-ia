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
    │   ├── test_app.py               # Testes simulados do laço e do fluxo de túnel
    │   ├── test_client.py            # Testes simulados de configuração, HTTP e resposta
    │   └── test_login_devel.py       # Testes simulados do fluxo de login no Devel
    ├── .env.example                  # Configuração de exemplo para o acesso institucional
    ├── exec_app.py                   # Prepara a configuração e inicia a aplicação
    ├── requirements.txt              # Dependências com versões fixadas
    └── README.md                     # Instruções de instalação, execução e testes
```

---

## Quickstart / Como Executar

O acesso padrão utiliza o modelo institucional Devel via encaminhamento SSH. Para provedores que exigem autenticação por token, a aplicação também aceita a variável opcional `LLM_API_KEY` no `.env` (enviada como cabeçalho `Authorization: Bearer`).

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

Nos dois caminhos, o script cria o `.env` se necessário e pede o host institucional se ele ainda não estiver configurado. A aplicação verifica a porta local e abre o túnel se precisar. Informe o login do Devel e a frase de segurança da chave se forem solicitados. Digite a pergunta quando o campo de entrada aparecer.

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

Para evitar digitar o login do portal sempre que abrir o túnel, preencha as variáveis opcionais abaixo no seu `.env` local. Use aspas na senha se ela tiver espaços ou `#`. O arquivo é ignorado pelo Git e armazena a senha em texto claro.

```dotenv
DEVEL_EMAIL=
DEVEL_SENHA=
```

O script pede no terminal os campos que estiverem vazios. Se o envio do login devolver a página de entrada ou retornar HTTP 401 ou 403, o script recarrega o formulário e oferece uma nova tentativa para os campos digitados. Use `Ctrl+C` para encerrar. Se os dois campos já estiverem configurados, o script encerra com uma orientação para revisar o `.env`. Os demais erros HTTP exibem o código e encerram o script. O SSH continua pedindo a frase de segurança da chave quando necessário.

### 5. Abrir o túnel antes de executar a aplicação

Prepare a chave SSH e inicie o contêiner no Devel conforme o [artigo sobre o acesso ao LLM institucional](https://ead.hardware.org.br/mod/forum/discuss.php?d=1323). Os comandos `ssh` e `cloudflared` precisam estar disponíveis no computador local.

Ao usar o Dockerfile deste repositório, informe no ambiente do contêiner a variável `HOST_API_LLM_INTERNO` com o mesmo valor do `.env` local. O servidor SSH usa esse nome para limitar o encaminhamento ao LLM na porta `9001`.

No primeiro terminal, dentro de `p0_primeiro_fluxo_llm` e com o ambiente virtual ativo, execute o script incluído no repositório.

```bash
python ../infra/tunel_devel/abrir_tunel_cloudflare.py
```

Informe as credenciais do portal que não estiverem configuradas no `.env`. Se o SSH pedir a frase de segurança da chave, informe-a também. Mantenha esse terminal aberto enquanto usa a aplicação. Ao terminar, pressione `Ctrl+C` nesse terminal para fechar o túnel.

### 6. Executar a aplicação (CLI)

Em um segundo terminal, entre em `p0_primeiro_fluxo_llm` e ative a `.venv` criado usando o comando do [passo 2](#2-criar-e-ativar-o-ambiente-virtual). Depois, execute a aplicação no mesmo terminal.

```bash
python -m src.app
```

Se aparecer `No module named 'dotenv'`, confira se você ativou a `.venv` nesse mesmo terminal e instalou as dependências conforme o passo 3. O pacote `python-dotenv` é instalado na `.venv` e importado como `dotenv`.

Antes de pedir a dúvida, a aplicação verifica a porta local `19001` para reutilizar o encaminhamento. Se a porta estiver fechada, tenta abrir o túnel no próprio terminal e encerra essa conexão ao sair.

Você pode enviar várias perguntas na mesma execução. Cada pergunta é enviada separadamente. Digite `sair` para encerrar a sessão.

### 7. Executar os testes automatizados (integração simulada)

Na pasta `p0_primeiro_fluxo_llm`, com a `.venv` ativa, execute o pytest como módulo do Python. Assim, a pasta atual fica disponível para os testes importarem `src`.

```bash
python -m pytest
```

Todos os testes da suíte atual rodam **100% offline** usando simulação (`monkeypatch`), sem acessar o Devel ou a internet:

- `tests/test_app.py`: fluxo principal do terminal, abertura e queda do túnel SSH antes do envio e preservação do código de saída.
- `tests/test_client.py`: montagem pura da solicitação, validação local de configuração (`LLM_TIMEOUT_SECONDS`, `LLM_VERIFICAR_TLS`, `LLM_THINK`, `LLM_API_URL`, `LLM_MODEL`), códigos HTTP (`401`, `403`, `404`, `429`, `500`, `502`, `503`, `504` e fallback), timeout, falha de conexão, resposta vazia, JSON inválido e formato inesperado.
- `tests/test_login_devel.py`: tentativas de login interativo e recusa controlada com credenciais configuradas.

Os testes reais contra o modelo institucional no Devel são executados manualmente via `python -m src.app` ou `python exec_app.py`, com resultados registrados na seção [Testes reais realizados](#testes-reais-realizados).

### 8. Tudo mastigado

Para executar a aplicação em um único terminal, prepare a chave SSH, inicie o contêiner no Devel e rode o comando na pasta `p0_primeiro_fluxo_llm`.

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

### Campo da pergunta sem entrada visível no Git Bash

No Windows, o campo `>` pode deixar de exibir o que você digita no Git Bash (`MINGW64`) depois que o SSH pede a frase da chave. O sintoma apareceu quando `exec_app.py` abriu o túnel e a aplicação no mesmo terminal. A causa exata ainda não foi confirmada.

Se isso acontecer, encerre a execução atual com `Ctrl+C`. Abra o túnel no primeiro Git Bash conforme o [passo 5](#5-abrir-o-túnel-antes-de-executar-a-aplicação) e mantenha esse terminal aberto. Em um segundo Git Bash, na pasta `p0_primeiro_fluxo_llm`, execute `uv run exec_app.py`. No teste com os terminais separados, foi possível digitar e enviar a pergunta pelo túnel já aberto.

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

