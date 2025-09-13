import os
import groq 
from copy import deepcopy
from groq import Groq


import cohere
# Make sure you have set this in your environment first, e.g.:
#   export GROQ_API_KEY="your_api_key_here"   (Linux/macOS)
#   setx GROQ_API_KEY "your_api_key_here"     (Windows PowerShell)

# Initialize Groq Client for the Llama3 AI model
ai = Groq()
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
            "amount": "number - The amount to withdraw.",
            "portfolio": "string - The name of the portfolio to withdraw from."
        },
        "format": "amount | portfolio"
    },

    "INVEST": {
        "description": "Use this when the user asks to invest a specific amount of money into a specific investment portfolio. Example: 'Invest $50 in my growth fund.'",
        "parameters": {
            "amount": "number - The amount to invest.",
            "portfolio": "string - The name of the portfolio to invest in."
        },
        "format": "amount | portfolio"
    },

    "NEED_MORE_INFO": {
        "description": "Use this ONLY when the user clearly wants to perform an action (e.g., invest, withdraw, set target, etc.) but has NOT provided enough details (missing amount, portfolio, or item). Ask a SPECIFIC follow-up question to gather what is missing. Example: User says 'I want to invest,' but does not say how much or where.",
        "parameters": {
            "question": "string - The specific clarifying question to ask the user."
        },
        "format": "question"
    }
}



from level import __clients, register_client, get_client_info, get_messages, get_target, set_target, set_daily_saving, done_daily_saving, done_weekly_invest

def do_action(clientId, action: str, params: list[str]):
    action = action.split("</think>")[1].strip() if "</think>" in action else action.strip()
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
        if len(params) != 0:
            print(f"Error: DONE_DAILY_SAVING requires no parameters, got {len(params)}")
            return False, None
        done_daily_saving(clientId)
        print(f"Marked daily saving as done for client {clientId}")

    elif "DONE_WEEKLY_INVEST" in action.upper():
        if len(params) != 0:
            print(f"Error: DONE_WEEKLY_INVEST requires no parameters, got {len(params)}")
            return False, None
        done_weekly_invest(clientId)
        print(f"Marked weekly invest as done for client {clientId}")

    elif "NO_ACTION" in action.upper():
        if len(params) != 0:
            print(f"Error: NO_ACTION requires no parameters, got {len(params)}")
            return False, None
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
        if len(params) != 0:
            print(f"Error: GET_INFO requires no parameters, got {len(params)}")
            return False, None
        info = get_client_info(clientId)

        print(info)



        return False, "Info provided from server. Let the user knwo that it has been sent."
    else:
        print(f"Error: Unknown action '{action}'")
        return False, None

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
        "- ALWAYS respond with the ACTION NAME, followed by its parameters in the specified format.\n"
        "- The format is: ACTION_NAME | param1 | param2 | ... | paramN\n"
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
    completion = ai.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=action_messages,
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None
    )

    cohere_response = co.chat(
        model="command-a-03-2025", 
        messages=action_messages    
    )

    print("Cohere Response:", cohere_response.message.content[0].text)

    action_response = ""
    for chunk in completion:
        action_response += chunk.choices[0].delta.content or ""

    print("Action Response:", action_response.split("|")[0].strip())
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
        if message:
            messages.append({
                "role": "system",
                "content": message
            })
        else:
            messages.append({
                "role": "system",
                "content": f"Let the user know that the previous request failed to be processed. Ask them to try again. Make it short and polite."
            })

    # REPLY
    completion = ai.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=messages,
        temperature=1,
        max_completion_tokens=512,
        top_p=1,
        stream=True,
        stop=None
    )
    

    cohere_response = co.chat(
        model="command-a-03-2025", 
        messages=messages  
    )

    print("Cohere Response:", cohere_response.message.content[0].text)
    res = ""
    for chunk in completion:
        res += chunk.choices[0].delta.content or ""

    print("AI Response:", res)
    messages.append({
        "role": "assistant",
        "content": res
    })