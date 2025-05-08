import openai

def check_openai_usage():
    try:
        # Make an API request to get the usage info for the current billing period
        usage = openai.Usage.retrieve()
        
        # Extract token usage data (you can print the whole response for more detail)
        total_usage = usage['total_usage']['tokens']
        
        print(f"Total tokens used: {total_usage}")
        
        return total_usage
    
    except openai.error.OpenAIError as e:
        print(f"Error occurred while fetching usage: {e}")
        return None

if __name__ == "__main__":
    check_openai_usage()