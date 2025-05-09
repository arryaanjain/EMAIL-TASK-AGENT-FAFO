import requests
from datetime import datetime, timedelta
from config import Config

def get_token_data(auth_code):
    token_url = f"{Config.AUTHORITY}/oauth2/v2.0/token"
    data = {
        "client_id": Config.CLIENT_ID,
        "scope": " ".join(Config.SCOPE),
        "redirect_uri": Config.REDIRECT_URI,
        "grant_type": "authorization_code",
        "code": auth_code,
        "client_secret": Config.CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    return response.json()

def refresh_access_token(refresh_token):
    token_url = f"{Config.AUTHORITY}/oauth2/v2.0/token"
    data = {
        "client_id": Config.CLIENT_ID,
        "scope": " ".join(Config.SCOPE),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_secret": Config.CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    return response.json()
