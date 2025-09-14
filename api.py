import requests

BASE_URL = "https://2dcq63co40.execute-api.us-east-1.amazonaws.com/dev"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZWFtSWQiOiI4NjcxMzhhYi05ZDllLTQwZjAtODg1NC02YTgxMGVkY2FjMzMiLCJ0ZWFtX25hbWUiOiJEYW5uIiwiY29udGFjdF9lbWFpbCI6ImRhbmllbC5zdGV2YW51c0BtYWlsLnV0b3JvbnRvLmNhIiwiZXhwIjoxNzU4NjgyNzE4LjI4MTE3Nn0.gWnbXpQTt7s8K0bqxTdYEbUh6n2EGmjYSgNVfQki-mw"  # Replace with your key
CLIENTS_FILE = "clients.txt"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

class ClientAPI:
    @staticmethod
    def getTotalInvested(client_id: str) -> float:
        """
        Calculate the total amount invested across all portfolios for a given client.

        Parameters:
            client_id (str): The unique identifier of the client.
        Returns:
            float: Total amount invested across all portfolios.
        """

        portfolios_res = ClientAPI.list_portfolios(client_id)
        if not portfolios_res["success"]:
            return 0.0
        portfolios = portfolios_res["data"]
        total_invested = sum(portfolio.get("invested_amount", 0.0) for portfolio in portfolios)
        return total_invested

    @staticmethod
    def getCurrentValue(client_id: str) -> float:
        """
        Calculate the total amount invested across all portfolios for a given client.

        Parameters:
            client_id (str): The unique identifier of the client.
        Returns:
            float: Total amount invested across all portfolios.
        """

        portfolios_res = ClientAPI.list_portfolios(client_id)
        if not portfolios_res["success"]:
            return 0.0
        portfolios = portfolios_res["data"]
        total_invested = sum(portfolio.get("current_value", 0.0) for portfolio in portfolios)
        return total_invested

    @staticmethod
    def create_client(name: str, email: str, cash: float, portfolios: list = None):
        """
        Register a new client. On success, save the client ID into clients.txt.
        Returns a dict with success flag, status code, and data/error.
        """
        if portfolios is None:
            portfolios = []

        url = f"{BASE_URL}/clients"
        payload = {
            "name": name,
            "email": email,
            "cash": cash,
            "portfolios": portfolios
        }

        response = requests.post(url, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code == 201:  # Created
            client_id = data.get("id")
            if client_id:
                with open(CLIENTS_FILE, "a") as f:
                    f.write(client_id + "\n")
                print(f"✅ Client created with ID: {client_id} (saved to {CLIENTS_FILE})")
            return {"success": True, "status_code": 201, "data": data}

        elif response.status_code == 409:  # Conflict
            print("⚠️ Client already exists:", data)
            return {"success": False, "status_code": 409, "error": data}

        else:  # Other errors
            print(f"❌ Error {response.status_code}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}
    @staticmethod
    def get_client(client_id: str):
        """
        Retrieve details for a specific client by ID.
        Returns a dict with success flag, status code, and data/error.
        """
        url = f"{BASE_URL}/clients/{client_id}"

        response = requests.get(url, headers=HEADERS)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code == 200:  # OK
            print(f"✅ Client {client_id} details retrieved successfully.")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Error retrieving client {client_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

    @staticmethod
    def update_client(client_id: str, name: str = None, email: str = None):
        """
        Update an existing client by ID.
        Only 'name' and 'email' fields can be updated.
        Returns a dict with success flag, status code, and data/error.
        """
        url = f"{BASE_URL}/clients/{client_id}"
        payload = {}

        if name:
            payload["name"] = name
        if email:
            payload["email"] = email

        if not payload:
            raise ValueError("At least one of 'name' or 'email' must be provided")

        response = requests.put(url, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code in (200, 201):  # OK or Created
            print(f"✅ Client {client_id} updated successfully.")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Error updating client {client_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

    @staticmethod
    def deposit(client_id: str, amount: float):
        """
        Deposit money into a client's cash balance.

        Parameters:
            client_id (str): The unique identifier of the client.
            amount (float): Amount to deposit.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{BASE_URL}/clients/{client_id}/deposit"
        payload = {"amount": amount}

        response = requests.post(url, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code in (200, 201):
            print(f"✅ Deposited {amount} into client {client_id}")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Error depositing into client {client_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

    @staticmethod
    def create_portfolio(client_id: str, portfolio_type: str, initial_amount: float):
        """
        Create a new investment portfolio for a client.
        The initial amount will be deducted from the client's cash balance.

        Parameters:
            client_id (str): The unique identifier of the client.
            portfolio_type (str): Strategy type ('aggressive_growth', 'growth', 'balanced', 'conservative', 'very_conservative').
            initial_amount (float): Initial investment amount.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{BASE_URL}/clients/{client_id}/portfolios"
        payload = {
            "type": portfolio_type,
            "initialAmount": initial_amount
        }

        response = requests.post(url, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code in (200, 201):
            print(response)
            print(f"✅ Portfolio '{portfolio_type}' created for client {client_id} with {initial_amount}")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Error creating portfolio for client {client_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

    @staticmethod
    def list_portfolios(client_id: str):
        """
        List all portfolios for a given client.

        Parameters:
            client_id (str): The unique identifier of the client.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{BASE_URL}/clients/{client_id}/portfolios"
        response = requests.get(url, headers=HEADERS)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code == 200:
            print(f"✅ Retrieved portfolios for client {client_id}")
            return {"success": True, "status_code": 200, "data": data}
        else:
            print(f"❌ Error retrieving portfolios for client {client_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

    @staticmethod
    def hasPortfolioType(client_id: str, portfolio_type: str) -> bool:
        """
        Check if a client has a portfolio of a specific type.

        Parameters:
            client_id (str): The unique identifier of the client.
            portfolio_type (str): Strategy type to check.

        Returns:
            bool: True if the portfolio type exists for the client, False otherwise.
        """

        portfolios_res = ClientAPI.list_portfolios(client_id)
        if not portfolios_res["success"]:
            return False
        portfolios = portfolios_res["data"]
        for portfolio in portfolios:
            if portfolio["type"] == portfolio_type:
                return True
        return False

    @staticmethod
    def get_portfolio(portfolio_id: str):
        """
        Get detailed information about a specific portfolio.

        Parameters:
            portfolio_id (str): The unique identifier of the portfolio.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{BASE_URL}/portfolios/{portfolio_id}"
        response = requests.get(url, headers=HEADERS)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code == 200:
            print(f"✅ Retrieved details for portfolio {portfolio_id}")
            return {"success": True, "status_code": 200, "data": data}
        else:
            print(f"❌ Error retrieving portfolio {portfolio_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

    @staticmethod
    def transfer_to_portfolio(portfolio_id: str, amount: float):
        """
        Transfer funds from a client's cash balance into a portfolio.

        Parameters:
            portfolio_id (str): The unique identifier of the portfolio.
            amount (float): Amount to transfer.

        Returns:
            dict: JSON response from the API.
        """
        url = f"{BASE_URL}/portfolios/{portfolio_id}/transfer"
        payload = {"amount": amount}

        response = requests.post(url, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code in (200, 201):
            print(f"✅ Transferred {amount} to portfolio {portfolio_id}")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Error transferring to portfolio {portfolio_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}


    @staticmethod
    def withdraw_from_portfolio(portfolio_id: str, amount: float):
        """
        Withdraw funds from a portfolio into a client's cash balance.

        Parameters:
            portfolio_id (str): The unique identifier of the portfolio.
            amount (float): Amount to withdraw.

        Returns:
            dict: JSON response from the API.
        """
        print(f"Withdrawing {amount} from portfolio {portfolio_id}")
        url = f"{BASE_URL}/portfolios/{portfolio_id}/withdraw"
        payload = {"amount": amount}

        response = requests.post(url, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code in (200, 201):
            print(f"✅ Withdrew {amount} from portfolio {portfolio_id}")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Error withdrawing from portfolio {portfolio_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

    @staticmethod
    def getPortfolioId_FromType(client_id: str, portfolio_type: str) -> dict | None:
        """
        Retrieve the portfolio ID for a given client and portfolio type.

        Parameters:
            client_id (str): The unique identifier of the client.
            portfolio_type (str): The type of portfolio (e.g., 'aggressive_growth').
        Returns:
            dict | None: The portfolio ID if found, otherwise None.
        """
        portfolios_res = ClientAPI.list_portfolios(client_id)
        if not portfolios_res["success"]:
            return None
        portfolios = portfolios_res["data"]
        for portfolio in portfolios:
            if portfolio["type"] == portfolio_type:
                return portfolio["id"]
        return None

    @staticmethod
    def get_portfolio_analysis(portfolio_id: str):
        """
        Retrieve portfolio analysis data, including trailing and calendar returns.

        Parameters:
            portfolio_id (str): The unique identifier of the portfolio.

        Returns:
            dict: JSON response containing analysis data.
        """
        url = f"{BASE_URL}/portfolios/{portfolio_id}/analysis"

        response = requests.get(url, headers=HEADERS)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code == 200:
            print(f"📊 Portfolio analysis for {portfolio_id} retrieved successfully.")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Error retrieving portfolio analysis for {portfolio_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}


    @staticmethod
    def simulate_portfolios(client_id: str, months: int):
        """
        Simulate all portfolios for a client over a specified number of months.

        Parameters:
            client_id (str): The unique identifier of the client.
            months (int): Number of months to simulate (max 12).

        Returns:
            dict: JSON response with simulation results.
        """
        if months < 1 or months > 12:
            raise ValueError("Months must be between 1 and 12.")

        url = f"{BASE_URL}/clients/{client_id}/simulate"
        payload = {"months": months}

        response = requests.post(url, headers=HEADERS, json=payload)

        try:
            data = response.json()
        except Exception:
            data = {"error": response.text}

        if response.status_code == 200:
            print(f"🧪 Simulation for {months} months completed for client {client_id}.")
            return {"success": True, "status_code": response.status_code, "data": data}
        else:
            print(f"❌ Simulation failed for client {client_id}: {data}")
            return {"success": False, "status_code": response.status_code, "error": data}

# response = ClientAPI.create_client(
#     name="Daniel",
#     email="daniel@example.com",
#     cash=1000.0,
#     portfolios=None
# )
