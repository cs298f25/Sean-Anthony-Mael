from dotenv import load_dotenv
import os
import requests

load_dotenv()

# Initializes the AI
# Load .env file from project root
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    # Try loading from current directory
    load_dotenv()

api_key = os.getenv('OPEN_AI_API')
if not api_key:
    raise ValueError(
        "OPEN_AI_API environment variable is not set.\n\n"
        "To fix this:\n"
        "1. Create a .env file in the project root directory\n"
        "2. Add the following line to .env:\n"
        "   OPEN_AI_API=sk-or-v1-your-api-key-here\n"
        "3. Get a free API key at: https://openrouter.ai/keys\n\n"
        "See .env.example for a template."
    )


def chat_with_ai(user_message):
    """
    Send a message to the AI and get a response using OpenRouter API.
    
    Args:
        user_message (str): The user's message/question
        
    Returns:
        str: The AI's response
    """
    # Validate API key is set
    if not api_key or api_key.strip() == '':
        raise Exception(
            "OPEN_AI_API key is not set or is empty. Please add it to your .env file.\n"
            "Get a free API key at https://openrouter.ai/keys"
        )
    
    # Check API key format (OpenRouter keys typically start with sk-or-v1-)
    if not api_key.startswith('sk-or-'):
        raise Exception(
            f"Invalid API key format. OpenRouter API keys should start with 'sk-or-v1-...'\n"
            f"Your key appears to start with: {api_key[:10]}...\n"
            "Please check your .env file and ensure you're using an OpenRouter API key.\n"
            "Get a free API key at https://openrouter.ai/keys"
        )
    
    # Get model from environment or use a default free model
    # meta-llama/llama-3.2-3b-instruct:free is generally the most reliable free model
    model = os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.2-3b-instruct:free')
    
    # OpenRouter API endpoint
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Prepare headers - OpenRouter requires these for tracking
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv('OPENROUTER_REFERER', 'http://localhost:8000'),
        "X-Title": os.getenv('OPENROUTER_TITLE', 'Zen Study Assistant'),
    }
    
    # System prompt to specialize the AI
    system_prompt = """You are Zen, a helpful study assistant and music expert. Your role is to:

1. Provide effective studying strategies and tips
2. Recommend music genres that match the user's study needs or mood
3. Suggest specific music recommendations for studying, focusing, relaxing, or motivation
4. Keep all responses SHORT, clear, and easy to read (2-4 sentences maximum)
5. Use bullet points or short paragraphs when helpful
6. Be friendly and encouraging

Always prioritize brevity and clarity. Format longer responses with line breaks for readability."""
    
    # Prepare the request payload
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    
    # List of fallback models to try if the primary model fails
    # Ordered by reliability - most reliable free models first
    # Note: Free models may have limited availability or rate limits
    fallback_models = [
        'meta-llama/llama-3.2-3b-instruct:free',  # Most reliable free model
        'microsoft/phi-3-mini-128k-instruct:free',  # Good alternative
        'google/gemini-2.0-flash-exp:free',  # When available
    ]
    
    # Additional fallback models (may not always be available)
    additional_fallbacks = [
        'mistralai/mistral-7b-instruct:free',
        'huggingface/zephyr-7b-beta:free',
        'google/gemini-flash-1.5-8b:free',
    ]
    
    # Combine fallbacks, but limit total attempts to avoid too many API calls
    # Only use first 2 additional fallbacks to keep total model attempts reasonable
    fallback_models += additional_fallbacks[:2]
    
    # Remove the primary model from fallback list if it's already there
    if model in fallback_models:
        fallback_models = [m for m in fallback_models if m != model]
    
    models_to_try = [model] + fallback_models
    
    last_error = None
    
    # Try each model until one works
    for attempt_model in models_to_try:
        try:
            # Update payload with current model
            payload['model'] = attempt_model
            
            # Make the API request
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            # Parse response regardless of status code
            try:
                result = response.json()
            except:
                # If we can't parse JSON, check status code
                if response.status_code != 200:
                    response.raise_for_status()
                raise Exception("Invalid JSON response from AI service")
            
            # Check for provider errors in response (even with 200 status)
            if 'error' in result:
                error_info = result['error']
                error_message = error_info.get('message', 'Unknown error')
                error_type = error_info.get('type', 'provider_error')
                error_code = error_info.get('code', response.status_code)
                
                # Check for specific error types that indicate model unavailability
                error_lower = error_message.lower()
                is_model_unavailable = (
                    'provider' in error_type.lower() or 
                    'provider' in error_message.lower() or
                    'no endpoints' in error_lower or
                    'endpoint not found' in error_lower or
                    'model not found' in error_lower or
                    'unavailable' in error_lower
                )
                
                # If it's a model availability error, try next model
                if is_model_unavailable:
                    last_error = f"Model '{attempt_model}' unavailable: {error_message}"
                    continue  # Try next model
                # Other errors, raise them
                raise Exception(f"AI service error: {error_message}")
            
            # Check status code for HTTP errors
            if response.status_code == 401:
                error_message = result.get('error', {}).get('message', 'Authentication failed')
                raise Exception(
                    f"AI service authentication failed (401): {error_message}\n\n"
                    "Please check your OPEN_AI_API key in the .env file.\n"
                    "Get a free API key at: https://openrouter.ai/keys"
                )
            
            # Raise for other HTTP errors
            if response.status_code != 200:
                response.raise_for_status()
            
            # Check if we have a valid response
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                if content:
                    return content
                last_error = f"Model {attempt_model} returned empty response"
                continue  # Try next model
            
            last_error = f"Model {attempt_model} returned invalid response format"
            continue  # Try next model
                
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            
            # For 401, don't try other models (auth issue)
            if status_code == 401:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('error', {}).get('message', 'Authentication failed')
                except:
                    error_message = 'Authentication failed'
                
                raise Exception(
                    f"AI service authentication failed (401): {error_message}\n\n"
                    "Please check your OPEN_AI_API key in the .env file.\n"
                    "Get a free API key at: https://openrouter.ai/keys"
                )
            
            # For other HTTP errors, try next model
            last_error = f"HTTP {status_code}: {str(e)}"
            continue
            
        except requests.exceptions.RequestException as e:
            # Network errors, try next model
            last_error = f"Network error: {str(e)}"
            continue
        except Exception as e:
            # Check if it's a retryable error
            error_str = str(e).lower()
            if 'authentication' in error_str or 'api key' in error_str:
                # Don't retry auth errors
                raise
            # Other errors, try next model
            last_error = str(e)
            continue
    
    # If we've tried all models and none worked
    error_details = f"Last error: {last_error}" if last_error else "Unknown error"
    
    raise Exception(
        f"All AI models failed. {error_details}\n\n"
        "This usually means:\n"
        "1. Free models are temporarily unavailable or at capacity\n"
        "2. Your API key may need credits for paid models\n"
        "3. Network connectivity issues\n\n"
        "Solutions:\n"
        "1. Wait a few moments and try again (free models may be rate-limited)\n"
        "2. Check your OPEN_AI_API key at https://openrouter.ai/keys\n"
        "3. Add credits to your OpenRouter account for more reliable access\n"
        "4. Check OpenRouter status at https://openrouter.ai\n"
        "5. Try setting OPENROUTER_MODEL in .env to a specific working model"
    )
