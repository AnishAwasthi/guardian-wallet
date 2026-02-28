import os
import uuid
from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv() # This tells Python to look for the .env file and load its contents
from circle.web3 import utils, developer_controlled_wallets

# 1. Load the secret keys from your .env file
load_dotenv()

# 2. Hand the keys to the Circle SDK
client = utils.init_developer_controlled_wallets_client(
    api_key=os.getenv("CIRCLE_API_KEY"),
    entity_secret=os.getenv("CIRCLE_ENTITY_SECRET")
)

app = FastAPI()

# Our database (now it will hold real wallet addresses)
agent_data = {}

# 3. The new magic door: Create a Wallet!
@app.get("/create-agent/{agent_id}")
def create_agent(agent_id: str):
    
    wallet_set_api = developer_controlled_wallets.WalletSetsApi(client)
    wallet_api = developer_controlled_wallets.WalletsApi(client)
    
    # A) Create a "Wallet Set" (a secure folder to hold this agent's wallets)
    # We use uuid4() to ensure Circle doesn't accidentally process the same request twice
    ws_req = developer_controlled_wallets.CreateWalletSetRequest.from_dict({
        "name": f"Agent_{agent_id}_Set",
        "idempotencyKey": str(uuid.uuid4())
    })
    ws_resp = wallet_set_api.create_wallet_set(ws_req)
    # Convert the object to a dictionary and grab the ID safely
    wallet_set_dict = ws_resp.data.wallet_set.model_dump(by_alias=True)
    wallet_set_id = wallet_set_dict.get("id")    
    
    # B) Provision the actual wallet on Ethereum Sepolia (a free test network)
    w_req = developer_controlled_wallets.CreateWalletRequest.from_dict({
        "blockchains": ["ETH-SEPOLIA"],
        "count": 1,
        "walletSetId": wallet_set_id,
        "accountType": "SCA", # Smart Contract Account (built for automation)
        "idempotencyKey": str(uuid.uuid4())
    })
    w_resp = wallet_api.create_wallet(w_req)
    # Convert the first wallet object to a dictionary and grab the address safely
    wallet_dict = w_resp.data.wallets[0].model_dump(by_alias=True)
    wallet_address = wallet_dict.get("address")    
    
    # C) Save the agent's new wallet and their allowance limit to our database
    agent_data[agent_id] = {
        "wallet_address": wallet_address,
        "allowance_limit": 50.00
    }
    
    return {
        "message": f"Agent {agent_id} successfully armed with a wallet.",
        "wallet_address": wallet_address
    }

# 4. Our original door, updated to show the new data
@app.get("/check-balance/{agent_id}")
def check_balance(agent_id: str):
    if agent_id in agent_data:
        return {"agent": agent_id, "data": agent_data[agent_id]}
    else:
        return {"error": "Agent not found. Create one first!"}

# ... (Keep all your previous code above this) ...

# 5. The Guardian Logic: Enforcing the Allowance
@app.post("/process-payment/{agent_id}")
def process_payment(agent_id: str, amount: float, destination_address: str):
    
    # A) Check if we know this agent
    if agent_id not in agent_data:
        return {"status": "DENIED", "reason": "Agent not found. Create one first."}
    
    agent = agent_data[agent_id]
    
    # B) THE RULE: Hard Cap Check
    if amount > agent["allowance_limit"]:
        return {
            "status": "DENIED", 
            "reason": f"Transaction blocked. ${amount} exceeds the daily limit of ${agent['allowance_limit']}."
        }
        
    # C) Execution (Mocked for now) & Database Update
    # *If we had testnet funds, we would execute the createTransaction function using the Circle SDK here*
    
    agent["allowance_limit"] -= amount
    
    return {
        "status": "APPROVED",
        "message": f"Successfully authorized ${amount} to {destination_address}.",
        "remaining_allowance": agent["allowance_limit"]
    }