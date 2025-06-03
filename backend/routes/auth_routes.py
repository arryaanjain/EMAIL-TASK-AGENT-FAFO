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

    response = requests.post(Config.TOKEN_ENDPOINT, data=token_data)
    if response.status_code != 200:
        return f"Token exchange failed: {response.text}", 400

    token_json = response.json()
    # Return tokens in URL parameters
    tokens = {
        "access_token": token_json.get("access_token"),
        "id_token": token_json.get("id_token")
    }
    redirect_url = f"{Config.FRONT_END_BASE_URL}/auth/callback?{urllib.parse.urlencode(tokens)}"
    return redirect(redirect_url)

@auth_bp.route("/logout")
def logout():
    # Clear session
    session.clear()
    
    # Construct Azure B2C logout URL
    logout_url = f"https://{Config.TENANT}.b2clogin.com/{Config.TENANT}.onmicrosoft.com/{Config.POLICY}/oauth2/v2.0/logout"
    params = {
        "post_logout_redirect_uri": f"{Config.FRONT_END_BASE_URL}/login"
    }
    
    return redirect(f"{logout_url}?{urllib.parse.urlencode(params)}")

@auth_bp.route("/status")
def auth_status():
    # Get token from Authorization header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"isAuthenticated": False})
    
    token = auth_header.split(' ')[1]
    try:
        # Validate token here
        return jsonify({"isAuthenticated": True})
    except:
        return jsonify({"isAuthenticated": False})