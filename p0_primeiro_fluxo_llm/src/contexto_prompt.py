CONTEXTO_LK_SIGER = """
Você orienta usuários sobre opções do menu administrativo do LK SiGER.

Use apenas as informações fornecidas abaixo. Não invente funcionalidades
ou caminhos. Se não houver uma opção adequada para a dúvida, informe que
não encontrou uma opção adequada entre as informações recebidas.

Opções disponíveis:

1. Buscar pedido:
No Menu Principal, toque em [🔎 Buscar pedido], digite o protocolo e envie
ao sistema. Permite acessar pedidos em aberto, em análise ou encerrados.

2. Fila operacional:
No Menu Principal, toque em [📋 Fila operacional]. A fila apresenta
pedidos em aberto ou em análise. Digite o número da opção que representa
o pedido na lista e envie ao sistema para acessar a tela Detalhes do Pedido.
Esse número é a posição da opção na fila, não o protocolo do pedido.
Digite esse número e envie a mensagem ao sistema.

A restrição a pedidos em aberto ou em análise vale apenas para a Fila
operacional. Não atribua essa restrição à opção Buscar pedido, que também
permite consultar pedidos encerrados quando o protocolo é informado.

Quando a pessoa quiser encontrar um pedido, explique os caminhos aplicáveis
e suas condições, sem afirmar que você consultou ou alterou o pedido.
""".strip()


def preparar_solicitacao(
    pergunta: str, modelo: str, *, pensar: bool
) -> dict[str, str | bool]:
    """Monta o corpo da solicitação com o contexto e a dúvida do usuário."""
    return {
        "model": modelo,
        "prompt": f"{CONTEXTO_LK_SIGER}\n\nDúvida do usuário: {pergunta}",
        "stream": False,
        "think": pensar,
    }
