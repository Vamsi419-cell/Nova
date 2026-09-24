from nova.loop import run_agent


def main():
    print("Nova v1.0 — CLI Research Assistant")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_input:
            continue

        run_agent(user_input)


if __name__ == "__main__":
    main()