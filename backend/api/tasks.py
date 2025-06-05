from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
from models.task import TaskResponse, TaskCreate, TaskExtractionResult
from services.ms_graph import MSGraphService
from .auth import get_current_user
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/calendar", response_model=List[TaskResponse])
async def list_calendar_events(
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's calendar events"""
    try:
        graph_service = MSGraphService(user.access_token)
        events = await graph_service.get_calendar_events()
        return [TaskResponse(**event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calendar", response_model=TaskResponse)
async def create_calendar_event(
    task: TaskCreate,
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new calendar event from task"""
    try:
        graph_service = MSGraphService(user.access_token)
        event_data = {
            "subject": task.title,
            "body": {"contentType": "text", "content": task.description},
            "start": {
                "dateTime": task.due_date.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": task.due_date.isoformat(),
                "timeZone": "UTC"
            }
        }
        response = await graph_service.create_calendar_event(event_data)
        return TaskResponse(**response, email_id=task.email_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/calendar/events", response_model=List[dict])
async def get_calendar_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=10, ge=1, le=50),
    include_details: bool = Query(default=False),
    user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get calendar events for a given time range"""
    try:
        graph_service = MSGraphService(user.access_token)
        events = await graph_service.get_calendar_events(
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            include_details=include_details
        )
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))