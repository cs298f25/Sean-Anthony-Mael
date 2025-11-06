from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPEN_AI_API')
if not api_key:
    raise ValueError("OPEN_AI_API environment variable is not set. Please create a .env file with your OpenRouter API key.")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=api_key,
)

completion = client.chat.completions.create(
#   extra_headers={
#     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
#     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
#   },
  extra_body={},
  model="google/gemma-3-27b-it:free",
  messages=[
              {
                "role": "user",
                "content": "What is the meaning of life?"
              }
            ]
)
print(completion.choices[0].message.content)