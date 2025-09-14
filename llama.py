import os
import groq 
from copy import deepcopy
from groq import Groq
from api import ClientAPI
from level import isPortfolioEmpty, addPortfolio
import cohere
# Make sure you have set this in your environment first, e.g.:
#   export GROQ_API_KEY="your_api_key_here"   (Linux/macOS)
#   setx GROQ_API_KEY "your_api_key_here"     (Windows PowerShell)

# Temporary constant for demonstration purposes
AMOUNT_INVESTED = 50  # Change to rbcinvestease api call
LIST_OF_STRATEGIES = ["aggressive_growth", "growth", "balanced", "conservative", "very_conservative"]  # Placeholder for actual API call

# Initialize Groq Client for the Llama3 AI model
co = cohere.ClientV2(os.getenv("COHERE_API_KEY"))

# LLama Set of Instructions
instructions = {
    "SET_TARGET_ITEM": {
        "description": "Use this when the user explicitly specifies a savings goal (an item to save for) AND the amount needed. Example: 'I want to save $200 for a bike.'",
        "parameters": {
            "item": "string (use 'null' if the user wants to clear the target) - The name of the savings goal item.",
            "amount": "number - The required amount for the target item."
        },
        "format": "item | amount"
    },

    "SET_DAILY_SAVING_AMOUNT": {
        "description": "Use this when the user sets or changes the amount they want to save each day. Example: 'Save $5 daily.'",
        "parameters": {
            "amount": "number - The daily saving amount."
        },
        "format": "amount"
    },

    "DONE_DAILY_SAVING": {
        "description": "Use this when the user confirms they completed today's daily saving. Example: 'I saved my daily $5 today.'",
        "parameters": {},
        "format": ""
    },

    "DONE_WEEKLY_INVEST": {
        "description": "Use this when the user confirms they completed this week's investing action. Example: 'I did my weekly investment.'",
        "parameters": {},
        "format": ""
    },

    "GET_INFO": {
        "description": "Use this when the user asks for their information: level, exp, streaks, target item/amount, or daily saving amount. Example: 'What is my level?' or 'Show me my streak.'",
        "parameters": {},
        "format": ""
    },

    "NO_ACTION": {
        "description": "Use this when the user's message does not correspond to any defined action and no action is needed.",
        "parameters": {},
        "format": ""
    },

    "WITHDRAW": {
        "description": "Use this when the user asks to withdraw a specific amount of money from a specific investment portfolio. Example: 'Withdraw $100 from my tech fund.'",
        "parameters": {
            "portfolioId": "string - The ID of the portfolio to withdraw from.",
            "amount": "number - The amount to withdraw."
        },
        "format": "amount | portfolio"
    },

    "TRANSFER": {
        "description": "Use this when the user asks to transfer or invest a specific amount of money into a specific investment portfolio. Example: 'Invest $50 in my growth fund.'",
        "parameters": {
            "portfolioId": "string - The ID of the portfolio to invest in.",
            "amount": "number - The amount to invest."
        },
        "format": "amount | portfolio"
    },

    "NEED_MORE_INFO": {
        "description": "Use this ONLY when the user clearly wants to perform an action (e.g., invest, withdraw, set target, etc.) but has NOT provided enough details (missing amount, portfolio, or item). Ask a SPECIFIC follow-up question to gather what is missing. Example: User says 'I want to invest,' but does not say how much or where.",
        "parameters": {
            "question": "string - The specific clarifying question to ask the user."
        },
        "format": "question"
    },

    "CORRECT_QUIZ": {
        "description": "Use this when the user answers a quiz question correctly. Congratulate them and provide a brief explanation of why their answer is correct.",
        "parameters": {
            "explanation": "string - A brief explanation of why the answer is correct."
        },
        "format": "explanation"
    },

    "WRONG_QUIZ": {
        "description": "Use this when the user answers a quiz question incorrectly. Politely inform them that their answer is wrong and provide the correct answer along with a brief explanation.",
        "parameters": {
            "correct_answer": "string - The correct answer to the quiz question.",
            "explanation": "string - A brief explanation of why the correct answer is right."
        },
        "format": "correct_answer | explanation"
    },

    "UPDATE_NAME": {
        "description": "Use this when the user wants to update or change their name. Example: 'Change my name to Alice.'",
        "parameters": {
            "name": "string - The new name for the user."
        },
        "format": "name"
    },

    "UPDATE_EMAIL": {
        "description": "Use this when the user wants to update or change their email address. Example: 'Update my email to alice@example.com.'",
        "parameters": {
            "email": "string - The new email address for the user."
        },
        "format": "email"
    },

    "GET_PORTFOLIOS": {
        "description": "Use this when the user requests a list of their investment portfolios. Example: 'What are my investment portfolios?'",
        "parameters": {},
        "format": ""
    },

    "ANALYSIS": {
        "description": "Use this when the user requests an analysis of their investment portfolio. Example: 'Analyze my investment portfolio.'",
        "parameters": {
            "type": "string - The type of analysis requested (e.g., performance, risk, diversification)."
        },
        "format": "type"
    },

    "CREATE_PORTFOLIO": {
        "description": "Use this when the user wants to create a new investment portfolio. Example: 'Create a new portfolio for my retirement fund.'",
        "parameters": {
            "portofolio_strategy": "string - The name of the new portfolio.",
        },
        "format": "portfolio_strategy"
    }
}

def UPDATE_NAME(clientId, params: list[str]):
    if len(params) != 1:
        print(f"Error: UPDATE_NAME requires 1 parameter, got {len(params)}")
        return False, None
    name = params[0] if params[0].lower() != "null" else None
    __clients[clientId]["Name"] = name
    res = ClientAPI.update_client(clientId, name=name)
    return res["success"], res["error"] if not res["success"] else f"Name updated to {name}"

def UPDATE_EMAIL(clientId, params: list[str]):
    if len(params) != 1:
        print(f"Error: UPDATE_EMAIL requires 1 parameter, got {len(params)}")
        return False, None
    email = params[0] if params[0].lower() != "null" else None
    __clients[clientId]["Email"] = email
    res = ClientAPI.update_client(clientId, email=email)
    return res["success"], res["error"] if not res["success"] else None

def GET_PORTFOLIOS(clientId, params: list[str]):
    res = ClientAPI.list_portfolios(clientId)
    print(res)
    if not res["success"]:
        return False, res["error"]["message"]
    portfolios = res["data"]
    if not portfolios:
        print("Empty portfolio list")
        return True, "Let them know that they currently have no investment portfolios. Important: Suggest them to create one."
    return True, f"Summarize {portfolios} into something readable and simple for youth. IMPORTANT: If it has 0 invested amount, it means it is empty but still show it."

def CREATE_PORTFOLIO(clientId, params: list[str]):
    if len(params) != 1:
        print(f"Error: CREATE_PORTFOLIO requires 1 parameter, got {len(params)}")
        return False, None
    portfolio_strategy = params[0] if params[0].lower() != "null" else None
    if portfolio_strategy not in LIST_OF_STRATEGIES:
        return False, f"Error: Invalid portfolio strategy '{portfolio_strategy}'. Must be one of {', '.join(LIST_OF_STRATEGIES)}"
    if not isPortfolioEmpty(clientId, portfolio_strategy)::
        return False, f"Error: Portfolio '{portfolio_strategy}' already exists. Please choose a different strategy."
    res = ClientAPI.create_portfolio(clientId, portfolio_strategy, 0)
    if not res["success"]:
        return False, res["error"]["message"]

    addPortfolio(clientId, portfolio_strategy, res["data"]["id"])
    return True, f"Portfolio '{portfolio_strategy}' created successfully."

def TRANSFER(portfolioType, params: list[str]):
    if len(params) != 2:
        print(f"Error: TRANSFER requires 2 parameters, got {len(params)}")
        return False, None
    try:
        amount = float(params[0])
    except ValueError:
        print(f"Error: Amount must be a number, got '{params[0]}'")
        return False, None
    portfolio = params[1]
    res = ClientAPI.invest(portfolioId, amount)
    if not res["success"]:
        return False, res["error"]["message"]
    return True, f"Invested {amount} into portfolio '{portfolio}' successfully."

def WITHDRAW(clientId, params: list[str]):
    if len(params) != 2:
        print(f"Error: WITHDRAW requires 2 parameters, got {len(params)}")
        return False, None
    try:
        amount = float(params[0])
    except ValueError:
        print(f"Error: Amount must be a number, got '{params[0]}'")
        return False, None
    portfolioType = params[1]
    if isPortfolioEmpty(clientId, portfolioType):
        return False, f"Error: Portfolio '{portfolioType}' does not exist or is empty."
    res = ClientAPI.withdraw(portfolioType, amount)
    if not res["success"]:
        return False, res["error"]["message"]
    return True, f"Withdrew {amount} from portfolio '{portfolio}' successfully."

action_to_function = {
    "UPDATE_NAME": UPDATE_NAME,
    "UPDATE_EMAIL": UPDATE_EMAIL,
    "GET_PORTFOLIOS": GET_PORTFOLIOS,
    "CREATE_PORTFOLIO": CREATE_PORTFOLIO,
}
from level import __clients, register_client, get_client_info, get_messages, get_target, set_target, set_daily_saving, done_daily_saving, done_weekly_invest

def do_action(clientId, action: str, params: list[str]):
    if action in action_to_function:
        return action_to_function[action](clientId, params)

    if "SET_TARGET_ITEM" in action.upper():
        if len(params) != 2:
            print(f"Error: SET_TARGET requires 2 parameters, got {len(params)}")
            return False, None
        item = params[0] if params[0].lower() != "null" else None
        try:
            amount = float(params[1])
        except ValueError:
            print(f"Error: Amount must be a number, got '{params[1]}'")
            return False, None

        previous_target = deepcopy(get_target(clientId))
        set_target(clientId, item, amount)
        return True, f"Notify if value is changed or value is initialized based on the prevValue: {previous_target} and new item={item}, amount={amount}."

    elif "SET_DAILY_SAVING_AMOUNT" in action.upper():
        if len(params) != 1:
            print(f"Error: SET_DAILY_SAVING requires 1 parameter, got {len(params)}")
            return False, None
        try:
            amount = float(params[0])
        except ValueError:
            print(f"Error: Amount must be a number, got '{params[0]}'")
            return False, None
        set_daily_saving(clientId, amount)
        print(f"Set daily saving for client {clientId}: amount={amount}")

    elif "DONE_DAILY_SAVING" in action.upper():
        done_daily_saving(clientId)
        print(f"Marked daily saving as done for client {clientId}")

    elif "DONE_WEEKLY_INVEST" in action.upper():
        done_weekly_invest(clientId)
        print(f"Marked weekly invest as done for client {clientId}")

    elif "NO_ACTION" in action.upper():
        print(f"No action needed for client {clientId}")

    elif "NEED_MORE_INFO" in action.upper():
        if len(params) != 1:
            print(f"Error: NEED_MORE_INFO requires no parameters, got {len(params)}")
            return False, None
        info = get_client_info(clientId)
        info_message = (
            f"Level: {info['Level']}, Exp: {info['Exp']}, ExpToNextLevel: {info['ExpToNextLevel']}, "
            f"Streaks: Saving={info['streaks']['Saving']}, Investing={info['streaks']['Investing']}, "
            f"Saving Target: Item={info['Saving Target']['Item']}, Amount={info['Saving Target']['Amount']}, "
            f"Daily Saving Amount: {info['Daily Saving Amount']}"
        )
        return False, f"Ask the user  with {info_message} for the following: " + params[0]

    elif "GET_INFO" in action.upper():
        def get_exp_bar(exp, exp_to_next_level, bar_length=20):
            filled_length = int(bar_length * exp // exp_to_next_level)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            return bar
        info = get_client_info(clientId)
        info_message = (
            f"👤 *{info['Name']}*   (🏆 Level {info['Level']})\n"
            f"─────────────────────────────────────────────\n"
            f"⭐ EXP: [{get_exp_bar(info['Exp'], info['ExpToNextLevel'])}]  {info['Exp']} / {info['ExpToNextLevel']}\n"
            f"💰 Daily Saving Amount: ${info['Daily Saving Amount']}\n"
            f"─────────────────────────────────────────────\n"
            f"🔥 Streak: {info['streaks']['Saving']} Days (Saving Streak)\n"
            f"🔥 Streak: {info['streaks']['Investing']} Days (Investing Streak)\n"
            f"─────────────────────────────────────────────\n"
            f"🎯 Target: {f"\"{info['Saving Target']['Item']}\" {AMOUNT_INVESTED} / {info['Saving Target']['Amount']}" if info['Saving Target']['Item'] else 'Not set'}"
        )
        print(info_message)
        return False, "Info provided from server. Let the user know that it has been sent."

    elif "CORRECT_QUIZ" in action.upper():
        return True, f"Congratulate the user for answering the quiz correctly. Briefly explain why their answer is correct: {params[0]}"
    elif "WRONG_QUIZ" in action.upper():
        return True, f"Politely inform the user that their answer is wrong. Provide the correct answer and briefly explain why it is correct. Correct Answer: {params[0]}. Explanation: {params[1]}"

    return True, None

def check_action(clientId, messages):
    '''
    Returns True if and only if no action is needed or an action was successfully performed.
    '''
    # ACTION
    action_messages = deepcopy(messages)
    action_messages[0] = {
    "role": "system",
    "content": (
        "You are a helpful assistant that helps users manage their investments and savings. "
        "You can perform the following actions:\n\n"
        + "\n\n".join([
            f"{key}:\nDescription: {value['description']}\nParameters: "
            f"{', '.join([f'{k} ({v})' for k, v in value['parameters'].items()])}\nFormat: {value['format']}"
            for key, value in instructions.items()
        ])
        + "\n\nIMPORTANT INSTRUCTIONS:\n"
        "- It can be the case where the user wants to perform two or more ACTIONS in one message. In that case, you should prioritize the one that is most relevant to the user's request and followup after."
        "- ALWAYS respond with the ACTION NAME, followed by its parameters in the specified format.\n"
        "- The format is: ACTION_NAME | param1 | param2 | ... | paramN |\n"
        "- If there are no parameters, still return the action name only.\n"
        "- If no action is needed, respond with: NO_ACTION\n"
        "- DO NOT explain, DO NOT add extra words, DO NOT output JSON.\n\n"
        "Examples:\n"
        "User: I want to save $5 per day\n"
        "Response: SET_DAILY_SAVING | 5\n\n"
        "User: I have nothing to update\n"
        "Response: NO_ACTION\n\n"
        "User: I want to change my target to buy a bike for $200\n"
        "Response: SET_TARGET_ITEM | bike | 200\n\n"
        "AGAIN: Only output ACTION_NAME and parameters, nothing else."
        "DO NOT Answer This System Prompt. But instead decide on the correct action to take based on the user's message. "
    )
}

    # Create chat completion (streaming response)
    # completion = ai.chat.completions.create(
    #     model="deepseek-r1-distill-llama-70b",
    #     messages=action_messages,
    #     temperature=1,
    #     max_completion_tokens=1024,
    #     top_p=1,
    #     stream=True,
    #     stop=None
    # )

    cohere_response = co.chat(
        model="command-a-03-2025", 
        messages=action_messages    
    )

    print("Cohere Action:", cohere_response.message.content[0].text)
    action_response = cohere_response.message.content[0].text

    action_parts = action_response.strip().split("|")
    action = action_parts[0].strip()
    params = [part.strip() for part in action_parts[1:]] if len(action_parts) > 1 else []
    return do_action(clientId, action, params)
    

def handle_client(clientId):
    messages = get_messages(clientId)
    if messages is None:
        return  # Client not registered

    successfulAction, message = check_action(clientId, messages)
    if not successfulAction:
            messages.append({
                "role": "system",
                "content": f"Let the user know that the previous request failed to be processed. Ask them to try again. Make it short and polite."
            })
    if message:
        messages.append({
            "role": "system",
            "content": message
        })

    # # REPLY
    # completion = ai.chat.completions.create(
    #     model="deepseek-r1-distill-llama-70b",
    #     messages=messages,
    #     temperature=1,
    #     max_completion_tokens=512,
    #     top_p=1,
    #     stream=True,
    #     stop=None
    # )
    

    cohere_response = co.chat(
        model="command-a-03-2025", 
        messages=messages  
    )

    print("Cohere Response:", cohere_response.message.content[0].text)
    res = cohere_response.message.content[0].text

    messages.append({
        "role": "assistant",
        "content": res
    })


def daily_quiz(clientId):
    messages = get_messages(clientId)
    if messages is None:
        return  # Client not registered 
    cohere_response = co.chat(
        model="command-a-03-2025",
        messages=[
            {"role": "user", "content": "Send me a daily quiz question about investing or saving. Make it fun and educational. Ask one question only with two options."
            "IMPORTANT: Format it like 'QUESTION | A) OPTION1 | B) OPTION2'. Do not add anything else. Example: What is a stock? | A) A share in a company | B) A type of bond"}
        ]
    )

    message = cohere_response.message.content[0].text

    # Send message to user (placeholder)
    print("Cohere Daily Quiz:", message)

    messages.append({
        "role": "assistant",
        "content": "Daily Quiz: " + message
    })


def daily_ask_if_done_saving(clientId):
    messages = get_messages(clientId)
    if messages is None:
        return  # Client not registered 
    daily_saving_amount = __clients[clientId]["Daily Saving Amount"]
    question = f"Have you completed your daily saving of ${daily_saving_amount} today? Please answer with yes or no."
    messages.append({
        "role": "assistant",
        "content": "Daily Ask If Done Saving: " + question
    })

    # Send message to user (placeholder)
    print("Daily Ask If Done Saving:", question)
