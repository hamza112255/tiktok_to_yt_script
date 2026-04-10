"""
Helper script to encode credentials for Railway environment variables
"""
import base64
import json

# Read the files
with open('client_secret.json', 'r') as f:
    client_secret = f.read()

with open('token.json', 'r') as f:
    token = f.read()

# Encode to base64
client_secret_b64 = base64.b64encode(client_secret.encode('utf-8')).decode('utf-8')
token_b64 = base64.b64encode(token.encode('utf-8')).decode('utf-8')

print("="*60)
print("COPY THESE TO RAILWAY ENVIRONMENT VARIABLES")
print("="*60)
print("\nCLIENT_SECRET_B64:")
print(client_secret_b64)
print("\n" + "="*60)
print("\nTOKEN_B64:")
print(token_b64)
print("\n" + "="*60)
print("\nInstructions:")
print("1. Go to Railway dashboard")
print("2. Click your service → Variables")
print("3. Add new variable: CLIENT_SECRET_B64")
print("4. Paste the CLIENT_SECRET_B64 value above")
print("5. Add new variable: TOKEN_B64")
print("6. Paste the TOKEN_B64 value above")
print("7. Save and redeploy")
print("="*60)
