from flask import Blueprint, redirect, request, jsonify
from config import Config
from services.token_utils import get_token_data
from datetime import datetime, timedelta
import requests
import urllib.parse

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
def callback():
    from models.user import User
    from db import db
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "No code in request"}), 400

    token_data = get_token_data(code)

    if "access_token" not in token_data:
        return jsonify({"error": "Failed to fetch token", "details": token_data}), 400

    # Decode the access token to get user email
    headers = {'Authorization': f"Bearer {token_data['access_token']}"}
    user_info = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers).json()
    email = user_info.get("userPrincipalName")

    if not email:
        return jsonify({"error": "Could not retrieve user email"}), 400

    expires_in = int(token_data['expires_in'])
    expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)

    # Save or update user in DB
    user = User.query.filter_by(email=email).first()
    if user:
        user.access_token = token_data['access_token']
        user.refresh_token = token_data['refresh_token']
        user.token_expires = expiry_time
    else:
        user = User(
            email=email,
            access_token=token_data['access_token'],
            refresh_token=token_data['refresh_token'],
            token_expires=expiry_time,
        )
        db.session.add(user)

    db.session.commit()
    return jsonify({"message": f"User {email} logged in successfully."})
