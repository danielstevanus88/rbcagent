from copy import deepcopy

# Constant
EXP_STREAK_DAILY_SAVING = 20
EXP_STREAK_WEEKLY_INVEST = 50

#__clients: A dictionary of clients id mapped to client information clientInfo
__clients = {}

# clientInfo default value
clientInfo_default = {
    "Name": "John Doe",
    "Level": 1,
    "Exp": 0,
    "ExpToNextLevel": 100,
    "streaks" : {
        "Saving" : 0,
        "Investing" : 0
    },
    "Saving Target": {
        "Item": "NOT SET YET", 
        "Amount": 0,
    },
    "Daily Saving Amount": 5,
    "Messages": [{
        "role": "system",
        "content": "You are a Investment and Saving assistant made for youth, assisting youth in managing their portfolios, savings, and investments on RBCAgent. You should always respond in a short but clear, unless it require long explanation."
        "IMPORTANT: Assume RBCAgent is my application and that you have access to the client info, which includes the user’s Level (current level in the system), Exp (accumulated experience points), Streaks (Saving = consecutive daily savings completed, Investing = consecutive weekly investments completed), Saving Target (Item = what the user is saving for, Amount = how much is needed to reach that goal), Daily Saving Amount (the fixed amount the user commits to save each day), and Messages (the conversation history, starting with a system message that defines the assistant’s role and tone). You are an investment and saving assistant for youth, focused on RBC InvestEase, and should always respond in a short but clear way unless the question requires a longer explanation."
    }]
}

# Client management functions
def register_client(clientId):
    if clientId in __clients:
        print(f'client with id {clientId} is already registered at the system')
        return
    __clients[clientId] = deepcopy(clientInfo_default)

# Get Info functions
def get_client_info(clientId):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return None
    return __clients[clientId]

def get_messages(clientId):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return None
    return __clients[clientId]["Messages"]

def get_streaks(clientId):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return None
    return __clients[clientId]["streaks"]

def get_target(clientId):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return None
    return __clients[clientId]["Saving Target"]
# Target functions
def set_target(clientId, item: str | None, amount: float):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return
    __clients[clientId]["Saving Target"]["Item"] = item
    __clients[clientId]["Saving Target"]["Amount"] = amount

# Daily saving functions
def set_daily_saving(clientId, amount: float):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return
    __clients[clientId]["Daily Saving Amount"] = amount

# Exp and Level functions
def exp_to_next_level(clientId, level):
    return 100 + level * 10

# Leveling functions
def add_exp(clientId, exp: int):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return
    __clients[clientId]["Exp"] += exp
    # Level up logic
    while __clients[clientId]["Exp"] >= __clients[clientId]["ExpToNextLevel"]:
        __clients[clientId]["Exp"] -= __clients[clientId]["ExpToNextLevel"]
        __clients[clientId]["Level"] += 1
        __clients[clientId]["ExpToNextLevel"] = exp_to_next_level(clientId, __clients[clientId]["Level"])



# Streaks functions
def done_daily_saving(clientId):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return
    __clients[clientId]["streaks"]["Saving"] += 1
    add_exp(clientId, EXP_STREAK_DAILY_SAVING)

def done_weekly_invest(clientId):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return
    __clients[clientId]["streaks"]["Investing"] += 1
    add_exp(clientId, EXP_STREAK_WEEKLY_INVEST)