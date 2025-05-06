import os
import time
from collections import deque
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils.email_reader import tokens_used, MAX_TOKENS_TOTAL

# Gemini Rate Limit Constants
REQUEST_LIMIT = 15
TIME_WINDOW = 60  # seconds
request_times = deque()

# LangChain prompt
email_prompt = PromptTemplate(
    input_variables=["subject", "body"],
    template="""
You are an assistant. Summarize this email and extract any tasks or follow-ups:
Subject: {subject}
Body: {body}
Return summary and bullet list of tasks.
"""
)

def enforce_gemini_rate_limit():
    """Enforces 15 requests per 60 seconds rule for Gemini free-tier."""
    current_time = time.time()
    while request_times and current_time - request_times[0] > TIME_WINDOW:
        request_times.popleft()

    if len(request_times) >= REQUEST_LIMIT:
        wait_time = TIME_WINDOW - (current_time - request_times[0])
        print(f"⏳ Rate limit hit. Waiting {wait_time:.2f} seconds...")
        time.sleep(wait_time)
        enforce_gemini_rate_limit()  # Re-check after waiting

    request_times.append(time.time())

def summarize_and_extract(subject, body):
    global tokens_used
    estimated_tokens = len(subject.split()) + len(body.split())
    
    if tokens_used + estimated_tokens > MAX_TOKENS_TOTAL:
        print("⚠️ Token limit would be exceeded. Skipping LLM call.")
        return None, None

    try:
        enforce_gemini_rate_limit()

        # Initialize Gemini via LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0,
            max_retries=5,
            request_timeout=60
        )

        chain = LLMChain(llm=llm, prompt=email_prompt)
        result = chain.run(subject=subject, body=body)

        parts = result.split("\nTasks:")
        summary = parts[0].replace("Summary:", "").strip()
        tasks = parts[1].strip() if len(parts) > 1 else "No tasks found."

        tokens_used += estimated_tokens
        return summary, tasks

    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return None, None
