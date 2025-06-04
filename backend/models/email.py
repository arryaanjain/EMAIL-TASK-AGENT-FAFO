from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

class EmailAddress(BaseModel):
    """Model for email addresses"""
    name: Optional[str] = None
    address: EmailStr

class Attachment(BaseModel):
    """Model for email attachments"""
    id: str
    name: str
    content_type: str
    size: int

class EmailBase(BaseModel):
    """Base email model with common fields"""
    id: str
    subject: str
    sender: EmailAddress
    received_time: datetime
    is_read: bool = False

class EmailProcess(BaseModel):
    """Model for email processing request"""
    subject: str
    body: str
    sender: EmailAddress
    received_time: datetime = Field(default_factory=datetime.now)
    importance: str = "normal"

class EmailResponse(EmailBase):
    """Model for email list response"""
    body_preview: str
    has_attachments: bool
    attachments: Optional[List[Attachment]] = None
    categories: Optional[List[str]] = None

class EmailDetail(EmailResponse):
    """Model for detailed email view"""
    body: str
    cc_recipients: Optional[List[EmailAddress]] = None
    bcc_recipients: Optional[List[EmailAddress]] = None
    conversation_id: Optional[str] = None

class EmailProcessResponse(BaseModel):
    """Model for email processing response"""
    summary: str
    tasks: List[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    processed_at: datetime = Field(default_factory=datetime.now)