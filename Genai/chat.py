
import argparse
import logging

from Genai.assistant import answer_question
from Genai.retrieval import load_transactions


def main() -> None:
    parser = argparse.ArgumentParser(description="DubaiEstate property-information assistant")
    parser.add_argument("question", nargs="*", help="Ask one question, or leave empty for chat mode")
    parser.add_argument("--show-prompt", action="store_true",
                        help="Also print the prompt an LLM would receive (nothing is sent)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    print("Loading dataset...")
    df, _ = load_transactions()

    def respond(question: str) -> None:
        answer = answer_question(df, question)
        print(f"\n[tool: {answer.route}]\n{answer.text}")
        if args.show_prompt:
            print("\n--- PROMPT (not sent anywhere) ---\n" + answer.prompt)

    if args.question:
        respond(" ".join(args.question))
        return

    print("Ask a question about 2026 Dubai transactions. Type 'quit' to exit.")
    while True:
        try:
            question = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"quit", "exit"}:
            break
        if question:
            respond(question)


if __name__ == "__main__":
    main()