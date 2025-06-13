from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import List, Optional
from models.email import EmailResponse, EmailStats, EmailCreate, EmailFilter
from services.ms_graph import MSGraphService
from .auth import get_current_user
from sqlalchemy.orm import Session
from db import get_db
import httpx
from config import Config
import requests

router = APIRouter()

@router.get("/test-msgraph")
async def test_msgraph_connection(
    request: Request,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Test Microsoft Graph connection"""
    try:
        # Get app-only token for Graph API
        token_data = {
            "client_id": Config.APP_ID,  # Use APP_ID instead of CLIENT_ID
            "client_secret": Config.CLIENT_SECRET,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials"
        }

        # Use the dedicated Graph token endpoint
        token_endpoint = Config.get_graph_token_endpoint()
        
        print(f"Requesting token from: {token_endpoint}")  # Debug logging
        print(f"Using client_id: {Config.APP_ID}")  # Debug logging
        
        token_response = requests.post(token_endpoint, data=token_data)
        
        if token_response.status_code != 200:
            print(f"Token response: {token_response.text}")  # Debug logging
            return {
                "status": "error",
                "message": f"Failed to get Graph token: {token_response.text}",
                "status_code": token_response.status_code
            }
            
        graph_token = token_response.json().get("access_token")
        
        # Test with users/count endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://graph.microsoft.com/v1.0/users/count",
                headers={
                    "Authorization": f"Bearer {graph_token}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code != 200:
                print(f"Graph API response: {response.text}")  # Debug logging
                return {
                    "status": "error",
                    "message": f"Failed to connect: {response.text}",
                    "status_code": response.status_code
                }
                
            return {
                "status": "success",
                "data": response.json()
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug logging
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/inbox", response_model=List[EmailResponse])
async def read_emails(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing access token")

    token = auth_header.split(" ")[1]

    # Make Graph API call
    async with httpx.AsyncClient() as client:
        graph_response = await client.get(
            "https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false",
            headers={"Authorization": f"Bearer {token}"}
        )

    if graph_response.status_code != 200:
        raise HTTPException(status_code=graph_response.status_code, detail=graph_response.text)

    return graph_response.json()


@router.get("/stats", response_model=EmailStats)
async def get_email_stats(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get email statistics including unread count, tasks, and meetings"""
    try:
        graph_service = MSGraphService(user.access_token)
        stats = await graph_service.get_email_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[EmailResponse])
async def search_emails(
    query: str,
    folder: Optional[str] = None,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search emails with given criteria"""
    try:
        graph_service = MSGraphService(user.access_token)
        results = await graph_service.search_emails(query, folder)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send", response_model=EmailResponse)
async def send_email(
    email: EmailCreate,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a new email"""
    try:
        graph_service = MSGraphService(user.access_token)
        sent_email = await graph_service.send_email(email)
        return sent_email
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{folder}", response_model=List[EmailResponse])
async def get_folder_emails(
    folder: str,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    filter: EmailFilter = None,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get emails from a specific folder (inbox, sent, drafts, etc.)"""
    try:
        graph_service = MSGraphService(user.access_token)
        emails = await graph_service.get_folder_emails(folder, skip, limit, filter)
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{email_id}/mark-read")
async def mark_as_read(
    email_id: str,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark an email as read"""
    try:
        graph_service = MSGraphService(user.access_token)
        await graph_service.mark_as_read(email_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{email_id}/process-tasks")
async def process_email_tasks(
    email_id: str,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process email for tasks using LangGraph"""
    try:
        graph_service = MSGraphService(user.access_token)
        email_content = await graph_service.get_email_content(email_id)
        # TODO: Implement LangGraph processing
        return {"status": "processing", "email_id": email_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

