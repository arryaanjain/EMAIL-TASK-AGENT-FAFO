import httpx
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException
from models.email import EmailResponse, EmailStats, EmailCreate, EmailFilter

class MSGraphService:
    BASE_URL = "https://graph.microsoft.com/v1.0"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    async def get_folder_emails(
        self,
        folder: str = "inbox",
        skip: int = 0,
        limit: int = 50,
        filter: Optional[EmailFilter] = None
    ) -> List[EmailResponse]:
        """Fetch emails from specified folder"""
        try:
            folder_id = self._get_folder_id(folder)
            params = {
                "$skip": skip,
                "$top": limit,
                "$orderby": "receivedDateTime desc",
                "$select": "id,subject,from,receivedDateTime,bodyPreview,isRead,categories"
            }

            if filter:
                filter_conditions = []
                if filter.is_read is not None:
                    filter_conditions.append(f"isRead eq {str(filter.is_read).lower()}")
                if filter.has_attachments is not None:
                    filter_conditions.append(f"hasAttachments eq {str(filter.has_attachments).lower()}")
                if filter_conditions:
                    params["$filter"] = " and ".join(filter_conditions)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/me/mailFolders/{folder_id}/messages",
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, 
                                     detail=response.text)

                emails = response.json().get("value", [])
                return [self._format_email_response(email) for email in emails]

        except Exception as e:
            raise HTTPException(status_code=500, 
                              detail=f"Failed to fetch emails: {str(e)}")

    async def get_email_stats(self) -> EmailStats:
        """Get email statistics"""
        try:
            async with httpx.AsyncClient() as client:
                # Get unread count
                unread_response = await client.get(
                    f"{self.BASE_URL}/me/mailFolders/inbox/messages?$filter=isRead eq false&$count=true",
                    headers=self.headers
                )
                
                # Get today's meetings
                today = datetime.utcnow().date().isoformat()
                meetings_response = await client.get(
                    f"{self.BASE_URL}/me/calendar/events?$filter=start/dateTime ge '{today}'",
                    headers=self.headers
                )

                # Get tasks (assuming tasks are emails with specific category)
                tasks_response = await client.get(
                    f"{self.BASE_URL}/me/messages?$filter=categories/any(c: c eq 'Task')",
                    headers=self.headers
                )

                return EmailStats(
                    unread_count=len(unread_response.json().get("value", [])),
                    meetings_today=len(meetings_response.json().get("value", [])),
                    task_count=len(tasks_response.json().get("value", []))
                )

        except Exception as e:
            raise HTTPException(status_code=500, 
                              detail=f"Failed to fetch email stats: {str(e)}")

    async def send_email(self, email: EmailCreate) -> EmailResponse:
        """Send a new email"""
        try:
            message = {
                "subject": email.subject,
                "body": {
                    "contentType": "HTML",
                    "content": email.body
                },
                "toRecipients": [{"emailAddress": {"address": to}} for to in email.to],
                "ccRecipients": [{"emailAddress": {"address": cc}} for cc in email.cc],
                "bccRecipients": [{"emailAddress": {"address": bcc}} for bcc in email.bcc]
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.BASE_URL}/me/sendMail",
                    headers=self.headers,
                    json={"message": message}
                )
                
                if response.status_code != 202:
                    raise HTTPException(status_code=response.status_code, 
                                     detail=response.text)

                return self._format_email_response(message)

        except Exception as e:
            raise HTTPException(status_code=500, 
                              detail=f"Failed to send email: {str(e)}")

    async def mark_as_read(self, email_id: str) -> None:
        """Mark an email as read"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.BASE_URL}/me/messages/{email_id}",
                    headers=self.headers,
                    json={"isRead": True}
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, 
                                     detail=response.text)

        except Exception as e:
            raise HTTPException(status_code=500, 
                              detail=f"Failed to mark email as read: {str(e)}")

    async def search_emails(self, query: str, folder: Optional[str] = None) -> List[EmailResponse]:
        """Search emails"""
        try:
            params = {
                "$search": f'"{query}"',
                "$select": "id,subject,from,receivedDateTime,bodyPreview,isRead,categories"
            }
            
            if folder:
                folder_id = self._get_folder_id(folder)
                url = f"{self.BASE_URL}/me/mailFolders/{folder_id}/messages"
            else:
                url = f"{self.BASE_URL}/me/messages"

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params
                )
                
                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, 
                                     detail=response.text)

                emails = response.json().get("value", [])
                return [self._format_email_response(email) for email in emails]

        except Exception as e:
            raise HTTPException(status_code=500, 
                              detail=f"Failed to search emails: {str(e)}")

    async def get_calendar_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
        include_details: bool = False
    ) -> List[dict]:
        """
        Fetch calendar events for a given time range.
        If no dates provided, defaults to next 7 days.
        """
        try:
            # Set default date range if not provided
            if not start_date:
                start_date = datetime.utcnow()
            if not end_date:
                end_date = start_date + timedelta(days=7)

            # Format dates for Microsoft Graph API
            start_str = start_date.isoformat() + 'Z'
            end_str = end_date.isoformat() + 'Z'

            # Build query parameters
            params = {
                "$top": limit,
                "$orderby": "start/dateTime",
                "$select": "id,subject,organizer,start,end,isAllDay,location"
            }

            if include_details:
                params["$select"] += ",body,attendees,categories,importance"

            # Add time range filter
            params["$filter"] = (
                f"start/dateTime ge '{start_str}' "
                f"and end/dateTime le '{end_str}'"
            )

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/me/calendar/events",
                    headers=self.headers,
                    params=params
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=response.text
                    )

                events = response.json().get("value", [])
                return [self._format_calendar_event(event) for event in events]

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch calendar events: {str(e)}"
            )

    def _format_calendar_event(self, event: dict) -> dict:
        """Format raw calendar event data"""
        return {
            "id": event.get("id"),
            "subject": event.get("subject"),
            "start": event.get("start", {}).get("dateTime"),
            "end": event.get("end", {}).get("dateTime"),
            "is_all_day": event.get("isAllDay", False),
            "organizer": {
                "name": event.get("organizer", {}).get("emailAddress", {}).get("name"),
                "email": event.get("organizer", {}).get("emailAddress", {}).get("address")
            },
            "location": event.get("location", {}).get("displayName"),
            "attendees": [
                {
                    "name": attendee.get("emailAddress", {}).get("name"),
                    "email": attendee.get("emailAddress", {}).get("address"),
                    "status": attendee.get("status", {}).get("response")
                }
                for attendee in event.get("attendees", [])
            ] if "attendees" in event else [],
            "categories": event.get("categories", []),
            "importance": event.get("importance", "normal"),
            "body": event.get("body", {}).get("content") if "body" in event else None
        }

    def _get_folder_id(self, folder: str) -> str:
        """Convert folder name to Microsoft Graph folder ID"""
        folder_mapping = {
            "inbox": "inbox",
            "sent": "sentitems",
            "drafts": "drafts",
            "deleted": "deleteditems",
            "archive": "archive"
        }
        return folder_mapping.get(folder.lower(), "inbox")

    def _format_email_response(self, email: dict) -> EmailResponse:
        """Format raw email data to EmailResponse model"""
        return EmailResponse(
            id=email.get("id", ""),
            subject=email.get("subject", ""),
            from_=email.get("from", {}).get("emailAddress", {}).get("address", ""),
            date=email.get("receivedDateTime", datetime.utcnow().isoformat()),
            snippet=email.get("bodyPreview", ""),
            is_read=email.get("isRead", False),
            labels=email.get("categories", []),
            folder=email.get("parentFolderId", "inbox")
        )