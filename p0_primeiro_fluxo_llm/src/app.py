"""Interface de Linha de Comando (CLI) para interacao com a aplicacao P0."""

from src.client import envia_prompt_llm


def main() -> None:
    """Ponto de entrada da CLI."""

    print("=" * 50)
    print("🤖 P0: Primeiro Fluxo com LLM")
    print("=" * 50)

    prompt = input("\nDigite o prompt a ser enviado para a LLM:\n> ").strip()

    if not prompt:
        print("Aviso: O prompt não pode ser vazio.")
        return

    print("\nEnviando requisição para a LLM, aguarde...")
    resposta = envia_prompt_llm(prompt)

    print("\n" + "-" * 50)
    print("Resposta:")
    print(resposta)
    print("-" * 50)


if __name__ == "__main__":
    main()

