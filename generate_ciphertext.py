import base64
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key

# 1. Your Credentials (loaded from .env)
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("CIRCLE_API_KEY")
entity_secret_hex = os.getenv("CIRCLE_ENTITY_SECRET")

print("Fetching Circle's Public Key...")
# 2. Ask Circle for their Public Key
response = requests.get(
    "https://api.circle.com/v1/w3s/config/entity/publicKey", 
    headers={"Authorization": f"Bearer {api_key}"}
).json()
public_key_pem = response['data']['publicKey']

print("Encrypting your Entity Secret...")
# 3. Encrypt your secret using RSA-OAEP with SHA-256 (Enterprise Standard)
public_key = load_pem_public_key(public_key_pem.encode('utf-8'))
ciphertext = public_key.encrypt(
    bytes.fromhex(entity_secret_hex),
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

print("\n=== PASTE THIS 684-CHARACTER STRING INTO THE CIRCLE CONSOLE ===")
print(base64.b64encode(ciphertext).decode('utf-8'))