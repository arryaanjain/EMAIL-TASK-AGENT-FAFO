from typing import List, Dict, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel

load_dotenv()

class TaskExtractionResult(BaseModel):
    """Model for task extraction results"""
    summary: str
    tasks: List[Dict[str, str]]
    confidence: float
    processed_at: datetime = datetime.now()

# Task extraction prompt
TASK_PROMPT = PromptTemplate(
    input_variables=["subject", "body"],
    template="""
    Analyze this email and extract tasks or action items. For each task, identify:
    1. The task description
    2. Any mentioned deadline or due date
    3. Priority level (if implied)
    4. Assignee (if specified)

    Email Subject: {subject}
    Email Body: {body}

    Provide:
    1. A brief summary of the email
    2. A structured list of tasks with their details
    3. Only include clear action items, not general information

    Format tasks as: [task description, due date, priority, assignee]
    """
)

class TaskExtractor:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.1,
            google_api_key=api_key,
            max_retries=3,
            convert_system_message_to_human=True
        )
        self.chain = LLMChain(llm=self.llm, prompt=TASK_PROMPT)
        
    def extract_tasks(self, subject: str, body: str) -> TaskExtractionResult:
        """
        Extract tasks from email content
        Args:
            subject: Email subject
            body: Email body text
        Returns:
            TaskExtractionResult object containing summary and extracted tasks
        """
        try:
            # Get raw LLM response
            result = self.chain.run(subject=subject, body=body)
            
            # Parse the response
            parts = result.split("\n\n")
            summary = parts[0].replace("Summary:", "").strip()
            
            # Extract tasks
            tasks = []
            for line in parts[1:]:
                if line.startswith("- "):
                    task_parts = line[2:].split(",")
                    if len(task_parts) >= 4:
                        tasks.append({
                            "description": task_parts[0].strip(),
                            "due_date": task_parts[1].strip(),
                            "priority": task_parts[2].strip(),
                            "assignee": task_parts[3].strip()
                        })

            return TaskExtractionResult(
                summary=summary,
                tasks=tasks,
                confidence=0.85 if tasks else 0.5
            )

        except Exception as e:
            raise ValueError(f"Task extraction failed: {str(e)}")

# Create singleton instance
task_extractor = TaskExtractor()

def process_email(subject: str, body: str) -> TaskExtractionResult:
    """
    Process an email and extract tasks
    Args:
        subject: Email subject
        body: Email body
    Returns:
        TaskExtractionResult containing summary and extracted tasks
    """
    return task_extractor.extract_tasks(subject, body)