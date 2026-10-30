import sys
from src.agent import run_agent_turn


def main():
    user_id = sys.argv[1] if len(sys.argv) > 1 else "default_user"
    print(f"=== Personal DeepAgent CLI (User: {user_id}) ===")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("\nEnter query > ").strip()
            if not query or query.lower() in ("exit", "quit"):
                break

            response = run_agent_turn(query=query, user_id=user_id)
            print("\n--- Response ---")
            print(response.result)

            if response.references:
                print("\n--- References ---")
                for i, ref in enumerate(response.references, 1):
                    print(f"{i}. [{ref.document_name}] {ref.title or ''} - {ref.source_url or 'N/A'}")
        except (KeyboardInterrupt, EOFError):
            break

    print("\nExiting DeepAgent. Goodbye!")


if __name__ == "__main__":
    main()
