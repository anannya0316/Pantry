"""
Interactive agent tester.

Run from the backend/ directory:
    python -m chatbot.test_agent

Commands during a session:
    reset   — start a fresh conversation thread
    quit    — exit
"""
import uuid
from chatbot.agent import run_agent

USER_ID = "test_user"


def _print_result(result: dict):
    print(f"\nAgent: {result['text']}")
    for ct in result.get("called_tools", []):
        success = result.get("success")
        flag = "✓" if success else ("✗" if success is False else "?")
        print(f"  [{flag}] {ct['tool_name']}  args={ct['arguments']}")
    print()


def main():
    chat_id = f"test-{uuid.uuid4().hex[:8]}"
    print("=" * 55)
    print("  Pantry agent tester")
    print(f"  thread: {chat_id}  |  user: {USER_ID}")
    print("  'reset' = new thread   'quit' = exit")
    print("=" * 55)
    print()

    while True:
        try:
            msg = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye.")
            break

        if not msg:
            continue

        if msg.lower() == "quit":
            break

        if msg.lower() == "reset":
            chat_id = f"test-{uuid.uuid4().hex[:8]}"
            print(f"\n[new thread: {chat_id}]\n")
            continue

        result = run_agent(
            user_message=msg,
            user_id=USER_ID,
            debug=True,
            chat_id=chat_id,
        )
        _print_result(result)


if __name__ == "__main__":
    main()
