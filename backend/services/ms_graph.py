import requests
from services.token_utils import refresh_access_token
from db import db
from datetime import datetime, timedelta
from fastapi import HTTPException

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

def fetch_unread_emails(user, limit: int = 10):
    """
    Fetch unread emails from user's inbox using Microsoft Graph API
    Args:
        user: User object containing access token
        limit: Number of emails to fetch (default: 10)
    Returns:
        List of unread emails
    """
    ensure_valid_token(user)
    
    headers = {
        "Authorization": f"Bearer {user.access_token}",
        "Content-Type": "application/json"
    }

    # Build query parameters
    params = {
        "$top": limit,  # Number of emails to return
        "$filter": "isRead eq false",  # Only unread emails
        "$orderby": "receivedDateTime desc",  # Most recent first
        "$select": "id,subject,bodyPreview,from,receivedDateTime,hasAttachments"  # Fields to return
    }

    try:
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me/messages",
            headers=headers,
            params=params
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Graph API error: {response.json().get('error', {}).get('message', 'Unknown error')}"
            )

        emails = response.json().get("value", [])
        
        # Transform the response to match our EmailResponse model
        formatted_emails = [{
            "id": email["id"],
            "subject": email["subject"],
            "body_preview": email["bodyPreview"],
            "sender": {
                "name": email["from"]["emailAddress"].get("name"),
                "address": email["from"]["emailAddress"]["address"]
            },
            "received_time": email["receivedDateTime"],
            "has_attachments": email["hasAttachments"],
            "is_read": False
        } for email in emails]

        return formatted_emails

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")
