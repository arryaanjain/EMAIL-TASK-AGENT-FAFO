import os
import time
import random
import google.generativeai as genai
from utils.email_reader import tokens_used, MAX_TOKENS_TOTAL

# Set your Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize model
model = genai.GenerativeModel("gemini-2.0-flash")

def summarize_and_extract(subject, body):
    global tokens_used
    estimated_tokens = len(subject.split()) + len(body.split())
    if tokens_used + estimated_tokens > MAX_TOKENS_TOTAL:
        print("⚠️ Token limit would be exceeded. Skipping Gemini call.")
        return None, None

    prompt = f"""
You are an assistant. Summarize this email and extract any tasks or follow-ups:
Subject: {subject}
Body: {body}
Return summary and bullet list of tasks.
"""

    # Implement exponential backoff for rate limiting
    max_retries = 5
    retry_count = 0
    base_delay = 1
    
    while retry_count < max_retries:
        try:
            response = model.generate_content(prompt)
            content = response.text

            parts = content.split("\nTasks:")
            summary = parts[0].replace("Summary:", "").strip()
            tasks = parts[1].strip() if len(parts) > 1 else "No tasks found."
            tokens_used += estimated_tokens
            return summary, tasks

        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower() or "quota" in str(e).lower():
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"⚠️ Rate limit exceeded after {max_retries} retries. Stopping.")
                    return None, None
                    
                # Calculate delay with exponential backoff and jitter
                delay = base_delay * (2 ** (retry_count - 1)) + random.uniform(0, 0.5)
                print(f"Rate limit hit. Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"❌ Gemini API call failed: {e}")
                return None, None
