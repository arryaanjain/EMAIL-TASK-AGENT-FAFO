from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def get_agent1_chain(llm):
    prompt = PromptTemplate(
        input_variables=["subject", "body"],
        template="""
        You are an assistant summarizing emails and extracting follow-up tasks.

        Subject: {subject}
        Body: {body}

        Respond like:
        Summary: ...
        Tasks:
        - ...
        - ...
        """
            )
    return LLMChain(llm=llm, prompt=prompt)

def test():
    print("test")
