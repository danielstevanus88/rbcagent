# import datetime
from datetime import datetime
from copy import deepcopy
from api import ClientAPI
# Constant
EXP_STREAK_DAILY_SAVING = 20
EXP_STREAK_WEEKLY_INVEST = 50

ID = "eec20378-12c4-4e55-9b0b-bdb292590b77"

#__clients: A dictionary of clients id mapped to client information clientInfo
__clients = {}
__portfolios = {}

def savePortfolioToFile(portfolioId, clientId):
    with open("portfolios.txt", "a") as f:
        f.write(f"{clientId}|{portfolioId}\n")

def savePortfolio(portfolioId, clientId):
    if clientId not in __portfolios:
        __portfolios[clientId] = []
    __portfolios[clientId].append(portfolioId)
    savePortfolioToFile(portfolioId, clientId)

def readPortfoliosFromFile():
    try:
        with open("portfolios.txt", "r") as f:
            lines = f.readlines()
            for line in lines:
                clientId, portfolioId = line.strip().split("|")
                if clientId not in __portfolios:
                    __portfolios[clientId] = []
                __portfolios[clientId].append(portfolioId)
    except FileNotFoundError:
        pass    

readPortfoliosFromFile()

def getPortfolioIdByType(clientId, portfolio_type: str) -> str | None:
    if clientId not in __clients or clientId not in __portfolios:
        print(f'client with id {clientId} is not registered at the system')
        return None
    for portfolioId in __portfolios[clientId]:
        portfolio_info = ClientAPI.get_portfolio(portfolioId)
        if portfolio_info["success"] and portfolio_info["data"]["type"] == portfolio_type:
            return portfolioId
    return None

# portfolio = {
#     "type": "aggressive_growth",
#     "clientId": ID
# }
# clientInfo default value
clientInfo_default = {
    "id": ID,
    "Name": ClientAPI.get_client(ID)["data"]["name"],
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
        "IMPORTANT: Assume RBCAgent is my fake application (no feature on it, all features access only through you, the Agent) and that you have access to the client info, which includes the user’s Level (current level in the system), Exp (accumulated experience points), Streaks (Saving = consecutive daily savings completed, Investing = consecutive weekly investments completed), Saving Target (Item = what the user is saving for, Amount = how much is needed to reach that goal), Daily Saving Amount (the fixed amount the user commits to save each day), and Messages (the conversation history, starting with a system message that defines the assistant’s role and tone). You are an investment and saving assistant for youth, focused on RBC InvestEase, and should always respond in a short but clear way unless the question requires a longer explanation."
    }],
    "Last Investment Time": None,
    "Last Saving Time": None,
    "Last Quiz Time": None
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
    # Check the last time saving was done to ensure it's daily
    last_saving_time = __clients[clientId]["Last Saving Time"]
    if last_saving_time is not None and last_saving_time.date() == datetime.now().date():
        print(f"Warning: client with id {clientId} has already done their daily saving today")
        return
    __clients[clientId]["Last Saving Time"] = datetime.now()
    __clients[clientId]["streaks"]["Saving"] += 1
    add_exp(clientId, EXP_STREAK_DAILY_SAVING)

def done_weekly_invest(clientId):
    if clientId not in __clients:
        print(f'client with id {clientId} is not registered at the system')
        return
    # Check the last time investment was done to ensure it's weekly
    last_investment_time = __clients[clientId]["Last Investment Time"]
    if last_investment_time is not None and last_investment_time.date() == datetime.now().date():
        print(f"Warning: client with id {clientId} has already done their weekly investment this week")
        return
    __clients[clientId]["Last Investment Time"] = datetime.now()
    __clients[clientId]["streaks"]["Investing"] += 1
    add_exp(clientId, EXP_STREAK_WEEKLY_INVEST)


# def getPortfolioId(clientId, portfolio_name: str) -> str | None:
#     if clientId not in __clients:
#         print(f'client with id {clientId} is not registered at the system')
#         return None
#     if portfolio_name not in __clients[clientId]["Portfolios"]:
#         print(f"Warning: client with id {clientId} does not have a portfolio named {portfolio_name}")
#         return None
#     return __clients[clientId]["Portfolios"][portfolio_name]

# def addPortfolio(clientId, portfolio_name: str, portfolio_id: str):
#     if clientId not in __clients:
#         print(f'client with id {clientId} is not registered at the system')
#         return
#     if portfolio_name in __clients[clientId]["Portfolios"]:
#         print(f"Warning: client with id {clientId} already has a portfolio named {portfolio_name}")
#         return
#     __clients[clientId]["Portfolios"][portfolio_name] = portfolio_id
