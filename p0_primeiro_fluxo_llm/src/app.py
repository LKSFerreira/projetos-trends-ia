"""Interface de linha de comando da aplicação P0."""

from src.client import envia_prompt_llm
from src.tunel_devel import preparar_tunel_devel, verificar_encaminhamento_devel


def main() -> None:
    """Ponto de entrada da CLI."""

    print("\n" + "=" * 100)
    print("🤖 P0: Primeiro Fluxo com LLM")
    print("=" * 100)

    try:
        with preparar_tunel_devel():
            while True:
                verificar_encaminhamento_devel()
                try:
                    prompt = input(
                        '\nDigite o prompt a ser enviado para a LLM ou "sair" para encerrar:\n> '
                    ).strip()
                except EOFError:
                    break

                if prompt.casefold() == "sair":
                    break
                verificar_encaminhamento_devel()
                if not prompt:
                    print("Aviso: O prompt não pode ser vazio.")
                    continue

                print("\nEnviando requisição para a LLM, aguarde...")
                resposta = envia_prompt_llm(prompt)
                print("\n" + "-" * 100)
                print("Resposta:")
                print(resposta)
                print("-" * 100)
    except RuntimeError as erro:
        raise SystemExit(str(erro)) from None

    print("\nSessão encerrada.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        raise SystemExit(130) from None

