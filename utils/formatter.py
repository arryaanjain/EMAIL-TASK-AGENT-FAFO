import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from utils.email_reader import tokens_used, MAX_TOKENS_TOTAL

# Define the prompt template for email summarization
email_prompt = PromptTemplate(
    input_variables=["subject", "body"],
    template="""
You are an assistant. Summarize this email and extract any tasks or follow-ups:
Subject: {subject}
Body: {body}
Return summary and bullet list of tasks.
"""
)

def summarize_and_extract(subject, body):
    global tokens_used
    estimated_tokens = len(subject.split()) + len(body.split())
    if tokens_used + estimated_tokens > MAX_TOKENS_TOTAL:
        print("⚠️ Token limit would be exceeded. Skipping LLM call.")
        return None, None

    try:
        # Initialize the Gemini model with LangChain
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0,
            max_retries=5,
            request_timeout=60
        )
        
        # Create a chain
        chain = LLMChain(llm=llm, prompt=email_prompt)
        
        # Run the chain
        result = chain.run(subject=subject, body=body)
        
        # Process the result
        parts = result.split("\nTasks:")
        summary = parts[0].replace("Summary:", "").strip()
        tasks = parts[1].strip() if len(parts) > 1 else "No tasks found."
        
        tokens_used += estimated_tokens
        return summary, tasks
        
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return None, None
