from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def get_agent2_chain(llm):
    prompt = PromptTemplate(
        input_variables=["raw_summary"],
        template="""
Format this email summary and tasks into a valid JSON string without any explanation, markdown, or additional text.

Input:
{raw_summary}

Output format:
{{
  "subject": "...",
  "summary": "...",
  "tasks": [
    {{
      "description": "...",
      "status": "pending"
    }}
  ]
}}
"""
    )
    return LLMChain(llm=llm, prompt=prompt)
