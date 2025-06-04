import os
import time
from collections import deque
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils.email_reader import tokens_used, MAX_TOKENS_TOTAL

class EmailProcessorAgent:
    # Gemini Rate Limit Constants
    REQUEST_LIMIT = 15
    TIME_WINDOW = 60  # seconds
    
    def __init__(self):
        self.request_times = deque()
        self.email_prompt = PromptTemplate(
            input_variables=["subject", "body"],
            template="""
            You are an assistant. Summarize this email and extract any tasks or follow-ups:
            Subject: {subject}
            Body: {body}
            Return summary and bullet list of tasks.
            """
        )
        
    def _enforce_gemini_rate_limit(self):
        """Enforces 15 requests per 60 seconds rule for Gemini free-tier."""
        current_time = time.time()
        while self.request_times and current_time - self.request_times[0] > self.TIME_WINDOW:
            self.request_times.popleft()

        if len(self.request_times) >= self.REQUEST_LIMIT:
            wait_time = self.TIME_WINDOW - (current_time - self.request_times[0])
            print(f"⏳ Rate limit hit. Waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
            self._enforce_gemini_rate_limit()  # Re-check after waiting

        self.request_times.append(time.time())

    def process_email(self, subject, body):
        """Process a single email to extract summary and tasks."""
        global tokens_used
        estimated_tokens = len(subject.split()) + len(body.split())
        
        if tokens_used + estimated_tokens > MAX_TOKENS_TOTAL:
            print("⚠️ Token limit would be exceeded. Skipping LLM call.")
            return None, None

        try:
            self._enforce_gemini_rate_limit()

            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=os.getenv("GEMINI_API_KEY"),
                temperature=0,
                max_retries=5,
                request_timeout=60
            )

            chain = LLMChain(llm=llm, prompt=self.email_prompt)
            result = chain.run(subject=subject, body=body)

            parts = result.split("\nTasks:")
            summary = parts[0].replace("Summary:", "").strip()
            tasks = parts[1].strip() if len(parts) > 1 else "No tasks found."

            tokens_used += estimated_tokens
            return summary, tasks

        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            return None, None