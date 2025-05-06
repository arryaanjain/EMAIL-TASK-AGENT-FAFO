import openai
import os
from dotenv import load_dotenv

load_dotenv()
# Load your API key from environment variable or directly (replace with your key)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Or you can replace with your actual API key like openai.api_key = 'your_api_key'

def test_openai_api():
    #print("API Key:", os.getenv("OPENAI_API_KEY"))
    try:
        # Sending a simple prompt to OpenAI's GPT-3.5 model (you can use gpt-4 or other models)
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Use gpt-4 if you want
            prompt="Hi",  # Simple test prompt
            max_tokens=10
        )

        # Print the response
        print("API Response:", response.choices[0].text.strip())

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_openai_api()
