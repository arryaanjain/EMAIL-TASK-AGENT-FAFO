from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskPriority(str, Enum):
    """Task priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskStatus(str, Enum):
    """Task status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskBase(BaseModel):
    """Base task model with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None

class TaskCreate(TaskBase):
    """Model for creating a new task"""
    email_id: str = Field(..., description="ID of the email this task was extracted from")
    confidence_score: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="AI confidence score for task extraction"
    )

class TaskUpdate(BaseModel):
    """Model for updating an existing task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee: Optional[str] = None
    status: Optional[TaskStatus] = None

class TaskResponse(TaskBase):
    """Model for task responses"""
    id: int
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime
    updated_at: datetime
    email_id: str
    confidence_score: float

class TaskExtractionResult(BaseModel):
    """Model for task extraction results"""
    email_id: str
    summary: str
    tasks: List[TaskCreate]
    processed_at: datetime = Field(default_factory=datetime.now)