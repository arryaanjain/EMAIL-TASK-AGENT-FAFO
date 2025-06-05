from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EmailFilter(BaseModel):
    is_read: Optional[bool] = None
    has_attachments: Optional[bool] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    labels: Optional[List[str]] = []

class EmailStats(BaseModel):
    unread_count: int
    task_count: int
    meetings_today: int

class EmailCreate(BaseModel):
    subject: str
    body: str
    to: List[str]
    cc: Optional[List[str]] = []
    bcc: Optional[List[str]] = []
    attachments: Optional[List[str]] = []

class EmailResponse(BaseModel):
    id: str
    subject: str
    from_: str
    date: datetime
    snippet: str
    is_read: bool
    labels: Optional[List[str]] = []
    folder: str