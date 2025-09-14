from level import register_client
from level import get_client_info, get_messages, get_streaks, get_target
from llama import check_action, handle_client, daily_quiz, daily_ask_if_done_saving
from level import ID
def getUserInput(clientId):
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit", "q"]:
        print("Exiting developer play.")
        exit()
    if user_input.lower() == "info":
        info = get_client_info(clientId)
        print(f"Client Info: {info}")
        return

    # Append user message
    messages = get_messages(clientId)
    messages.append({"role": "user", "content": user_input})

def getAIResponse(clientId):
    # Get AI response
    handle_client(clientId)

def developer_play():

    # Register a test client
    clientId = ID
    register_client(clientId)
    print(f"Registered client: {clientId}")


    # TODO: UNCOMMENT BELOW TO TEST DAILY ROUTINES
    # # 07.00am routine: Daily quiz
    # daily_quiz(clientId)  # Run daily quiz once at start
    # getUserInput(clientId)
    # getAIResponse(clientId)

    # TODO: UNCOMMENT BELOW TO TEST DAILY ROUTINES
    # # 09.00pm routine: Ask if done saving
    # daily_ask_if_done_saving(clientId)  # Ask if done saving once at start
    # getUserInput(clientId)
    # getAIResponse(clientId)


    # Start Conversation (Temporarily, until integrated with Whatsapp)
    while True:
        getUserInput(clientId)
        getAIResponse(clientId)


if __name__ == "__main__":

    developer_play()