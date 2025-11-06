from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initializes the AI
api_key = os.getenv('OPEN_AI_API')
if not api_key:
    raise ValueError("OPEN_AI_API environment variable is not set. Please create a .env file with your OpenRouter API key.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def chat_with_ai(user_message):
    """
    Send a message to the AI and get a response.
    
    Args:
        user_message (str): The user's message/question
        
    Returns:
        str: The AI's response
    """
    try:
        completion = client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error communicating with AI: {str(e)}")

