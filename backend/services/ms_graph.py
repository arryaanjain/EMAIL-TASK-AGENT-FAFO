import requests
from services.token_utils import refresh_access_token
from db import db
from datetime import datetime

def ensure_valid_token(user):
    if user.token_expires <= datetime.utcnow():
        new_token = refresh_access_token(user.refresh_token)
        if "access_token" in new_token:
            user.access_token = new_token["access_token"]
            user.refresh_token = new_token["refresh_token"]
            user.token_expires = datetime.utcnow() + timedelta(seconds=int(new_token["expires_in"]))
            db.session.commit()
        else:
            raise Exception("Could not refresh access token")

def get_calendar_events(user):
    ensure_valid_token(user)
    headers = {
        "Authorization": f"Bearer {user.access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://graph.microsoft.com/v1.0/me/events", headers=headers)
    return response.json()

def create_calendar_event(user, event_data):
    ensure_valid_token(user)
    headers = {
        "Authorization": f"Bearer {user.access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post("https://graph.microsoft.com/v1.0/me/events", headers=headers, json=event_data)
    return response.json()
