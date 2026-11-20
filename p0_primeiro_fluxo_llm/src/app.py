"""Interface de linha de comando da aplicação P0."""

from src.client import envia_prompt_llm
from src.tunel_devel import preparar_tunel_devel


def main() -> None:
    """Ponto de entrada da CLI."""

    print("=" * 100)
    print("🤖 P0: Primeiro Fluxo com LLM")
    print("=" * 100)

    prompt = input("\nDigite o prompt a ser enviado para a LLM:\n> ").strip()

    if not prompt:
        print("Aviso: O prompt não pode ser vazio.")
        return

    try:
        with preparar_tunel_devel():
            print("\nEnviando requisição para a LLM, aguarde...")
            resposta = envia_prompt_llm(prompt)
    except RuntimeError as erro:
        raise SystemExit(str(erro)) from None

    print("\n" + "-" * 100)
    print("Resposta:")
    print(resposta)
    print("-" * 100)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        raise SystemExit(130) from None

