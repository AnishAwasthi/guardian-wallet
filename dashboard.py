import streamlit as st
import requests

# Set the title of the web page
st.set_page_config(page_title="Guardian Wallet", page_icon="🛡️")
st.title("🛡️ The Guardian Wallet: Command Center")

# The URL where your FastAPI server is running
API_URL = "http://127.0.0.1:8000"

# --- SIDEBAR: Create an Agent ---
st.sidebar.header("1. Initialize Agent")
agent_id = st.sidebar.text_input("Agent Name", "Jarvis")

if st.sidebar.button("Create Agent Wallet"):
    with st.spinner("Talking to Circle & Minting Wallet..."):
        response = requests.get(f"{API_URL}/create-agent/{agent_id}")
        if response.status_code == 200:
            data = response.json()
            st.sidebar.success("Wallet Created!")
            st.sidebar.code(data['wallet_address'])
        else:
            st.sidebar.error("Failed to create agent.")

# --- MAIN DASHBOARD: Allowances & Payments ---
st.header(f"Active Agent: {agent_id}")
st.divider()

col1, col2 = st.columns(2)

# Column 1: Checking the Balance
with col1:
    st.subheader("💰 Current Policy")
    if st.button("Refresh Balance"):
        res = requests.get(f"{API_URL}/check-balance/{agent_id}")
        if res.status_code == 200 and "data" in res.json():
            allowance = res.json()["data"]["allowance_limit"]
            st.metric("Remaining Daily Allowance", f"${allowance:.2f}")
        else:
            st.warning("Agent not found. Create it in the sidebar first!")

# Column 2: Simulating a Spend Request
with col2:
    st.subheader("💸 Agent Spend Request")
    amount = st.number_input("Amount to Spend ($)", min_value=1.0, value=10.0, step=1.0)
    destination = st.text_input("Destination Address", "0xABC123...")
    
    if st.button("Process Payment"):
        # We send the data to the FastAPI backend to check the rules
        url = f"{API_URL}/process-payment/{agent_id}?amount={amount}&destination_address={destination}"
        res = requests.post(url)
        
        if res.status_code == 200:
            data = res.json()
            # UI responds based on our backend's logic!
            if data["status"] == "APPROVED":
                st.success(data["message"])
            else:
                st.error(data["reason"])