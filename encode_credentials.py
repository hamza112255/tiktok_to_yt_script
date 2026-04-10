"""
Helper script to encode credentials to base64 for Railway
"""
import base64
import json

# Your client_secret.json content
client_secret = {
    "installed": {
        "client_id": "818234388315-8alhni0fus896g9b9q77flvu9ri1jph3.apps.googleusercontent.com",
        "project_id": "my-video-conversion-app",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri"