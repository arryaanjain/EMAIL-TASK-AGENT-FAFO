from flask import Blueprint, redirect, request, session, jsonify
from config import Config
from services.token_utils import get_token_data
from datetime import datetime, timedelta
import requests
import urllib.parse
import jwt

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Step 1: Redirect user to Microsoft login
@auth_bp.route("/login")
def login():
    base_url = f"{Config.AUTHORITY}/oauth2/v2.0/authorize"
    params = {
        "client_id": Config.CLIENT_ID,
        "response_type": "code",
        "redirect_uri": Config.REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(Config.SCOPE),
    }
    login_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return redirect(login_url)

# Step 2: Handle callback from Microsoft
@auth_bp.route("/callback")
def auth_callback():
    code = request.args.get("code")
    if not code:
        return "Authorization code not found", 400

    token_data = {
        "grant_type": "authorization_code",
        "client_id": Config.CLIENT_ID,
        "client_secret": Config.CLIENT_SECRET,
        "code": code,
        "redirect_uri": Config.REDIRECT_URI,
        "scope": " ".join(Config.SCOPE),
    }

    # Exchange code for tokens
    response = requests.post(Config.TOKEN_ENDPOINT, data=token_data)
    if response.status_code != 200:
        return f"Token exchange failed: {response.text}", 400

    token_json = response.json()
    access_token = token_json.get("access_token")
    id_token = token_json.get("id_token")

    # Store in session or DB if needed
    session["access_token"] = access_token
    session["id_token"] = id_token

    return f"Access token acquired! ✅", 200