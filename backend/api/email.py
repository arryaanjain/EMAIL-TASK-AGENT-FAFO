from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from models.email import EmailProcess, EmailResponse
from services.ms_graph import fetch_unread_emails
from services.task_extraction import process_email, TaskExtractionResult
from .auth import get_current_user

router = APIRouter()

@router.get("/unread", response_model=List[EmailResponse])
async def get_unread_emails(
    limit: int = Query(default=10, ge=1, le=50),
    user = Depends(get_current_user)
):
    """
    Fetch unread emails
    Args:
        limit: Number of emails to fetch (1-50)
        user: Current authenticated user
    """
    try:
        emails = fetch_unread_emails(user, limit)
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/process", response_model=TaskExtractionResult)
async def process_emails(
    email_data: EmailProcess,
    user = Depends(get_current_user)
):
    """
    Process emails for task extraction
    Args:
        email_data: Email content to process
        user: Current authenticated user
    Returns:
        Extracted tasks and summary
    """
    try:
        result = process_email(email_data.subject, email_data.body)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))