from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.task import TaskResponse, TaskCreate, TaskExtractionResult
from services.ms_graph import get_calendar_events, create_calendar_event
from .auth import get_current_user

router = APIRouter()

@router.get("/calendar", response_model=List[TaskResponse])
async def list_calendar_events(user = Depends(get_current_user)):
    """Get user's calendar events"""
    try:
        events = get_calendar_events(user)
        return [TaskResponse(**event) for event in events]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calendar", response_model=TaskResponse)
async def create_calendar_event(
    task: TaskCreate,
    user = Depends(get_current_user)
):
    """Create a new calendar event from task"""
    try:
        # Convert TaskCreate to calendar event format
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
        response = create_calendar_event(user, event_data)
        return TaskResponse(**response, email_id=task.email_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))