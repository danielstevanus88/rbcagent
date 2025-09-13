from level import register_client
from level import get_client_info, get_messages, get_streaks, get_target
from llama import check_action, handle_client
def developer_play():

    # Register a test client
    clientId = "dev_client"
    register_client(clientId)
    print(f"Registered client: {clientId}")

    # Start Conversation
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting developer play.")
            break
        if user_input.lower() == "info":
            info = get_client_info(clientId)
            print(f"Client Info: {info}")
            continue

        # Append user message
        messages = get_messages(clientId)
        messages.append({"role": "user", "content": user_input})

        # Get AI response
        handle_client(clientId)


if __name__ == "__main__":
    developer_play()