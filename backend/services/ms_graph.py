import requests, httpx
from services.token_utils import refresh_access_token
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from db import get_db

async def ensure_valid_token(user, db: Session):
    """Ensure user token is valid, refresh if needed"""
    if user.token_expires <= datetime.utcnow():
        new_token = refresh_access_token(user.refresh_token)
        if "access_token" in new_token:
            user.access_token = new_token["access_token"]
            user.refresh_token = new_token["refresh_token"]
            user.token_expires = datetime.utcnow() + timedelta(seconds=int(new_token["expires_in"]))
            db.commit()
        else:
            raise HTTPException(status_code=401, detail="Could not refresh access token")

async def get_calendar_events(user, db: Session):
    """Get user's calendar events"""
    await ensure_valid_token(user, db)
    headers = {
        "Authorization": f"Bearer {user.access_token}",
        "Content-Type": "application/json"
    }
    response = requests.get("https://graph.microsoft.com/v1.0/me/events", headers=headers)
    return response.json()

async def create_calendar_event(user, event_data, db: Session):
    """Create a new calendar event"""
    await ensure_valid_token(user, db)
    headers = {
        "Authorization": f"Bearer {user.access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/events", 
        headers=headers, 
        json=event_data
    )
    return response.json()

async def fetch_unread_emails(user, db: Session, limit: int = 10):
    """
    Fetch unread emails from user's inbox using Microsoft Graph API
    Args:
        user: User object containing access token
        db: Database session
        limit: Number of emails to fetch (default: 10)
    Returns:
        List of unread emails
    """
    await ensure_valid_token(user, db)
    
    headers = {
        "Authorization": f"Bearer {user.access_token}",
        "Content-Type": "application/json"
    }

    # Build query parameters
    params = {
        "$top": limit,
        "$filter": "isRead eq false",
        "$orderby": "receivedDateTime desc",
        "$select": "id,subject,bodyPreview,from,receivedDateTime,hasAttachments"
    }

    try:
        # Use httpx instead of requests for async support
        async with httpx.AsyncClient() as client:
            response = await client.get(
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

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")