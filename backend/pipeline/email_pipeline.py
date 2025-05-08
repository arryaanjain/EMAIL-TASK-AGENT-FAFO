import os
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.agent1_summarizer import get_agent1_chain
from agents.agent2_json_formatter import get_agent2_chain
from utils.rate_limiter import enforce_rate_limit
from dotenv import load_dotenv

load_dotenv()

def build_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
        max_retries=5,
        request_timeout=60
    )

def run_email_pipeline(subject: str, body: str) -> str:
    enforce_rate_limit()
    llm = build_llm()

    agent1 = get_agent1_chain(llm)
    raw_summary = agent1.run({"subject": subject, "body": body})

    print("\n🤖 Agent 1 Output:\n", raw_summary)

    enforce_rate_limit()
    agent2 = get_agent2_chain(llm)
    formatted_json = agent2.run({"raw_summary": raw_summary})
    print("\nAgent 2 JSON:\n",formatted_json)
    return formatted_json
