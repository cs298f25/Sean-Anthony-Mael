from dotenv import load_dotenv
import os
import requests
import json

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

tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_and_store_artists_by_genre",
            "description": "Gets a list of artists for a specific genre, stores them in the database, and returns the list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "The music genre (e.g., 'rock', 'pop', 'synthpop')"
                    }
                },
                "required": ["genre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_and_store_tracks_by_genre",
            "description": "Gets song recommendations for a specific genre. Fetches artists for the genre, then fetches their top tracks, stores everything in the database, and returns the list of tracks. This is the BEST tool to use when the user asks for songs, music, or tracks in a specific genre.",
            "parameters": {
                "type": "object",
                "properties": {
                    "genre": {
                        "type": "string",
                        "description": "The music genre (e.g., 'rock', 'pop', 'synthpop', 'jazz', 'hip hop')"
                    }
                },
                "required": ["genre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_and_store_tracks_for_artist_by_name", 
            "description": "Gets a list of top tracks for a specific artist by their name, stores them, and returns the list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "The exact name of the artist (e.g., 'Daft Punk', 'The Beatles')"
                    }
                },
                "required": ["artist_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_and_store_chart_tracks",
            "description": "Gets the current most popular tracks from the GLOBAL chart (all genres combined). This returns the overall top tracks across all genres. If the user asks for songs in a SPECIFIC GENRE (e.g., 'hip hop songs', 'rock music'), use 'fetch_and_store_tracks_by_genre' instead. Only use this tool when the user asks for general/popular songs without specifying a genre.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_and_store_similar_artists",
            "description": "Gets a list of artists similar to a given artist, stores them, and returns the list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "artist_name": {
                        "type": "string",
                        "description": "The name of the artist to find similar artists for."
                    }
                },
                "required": ["artist_name"]
            }
        }
    }
]


system_prompt = """You are Zen, a helpful study assistant and music expert. Your role is to:

1. Provide effective studying strategies and tips.
2. Recommend music based on the user's needs or mood.
3. **Use the provided tools to find artists, tracks, charts, or similar artists when the user asks for music recommendations.**
4. After the tool returns data, present it clearly and concisely to the user.
5. Keep all responses SHORT, clear, and friendly (2-4 sentences maximum).
6. When presenting music recommendations, list 3-5 items maximum in a simple, readable format.

IMPORTANT:
- If the user asks for music, ALWAYS use a tool first. Do not make up artists or tracks.
- **When the user asks for SONGS, TRACKS, or MUSIC in a SPECIFIC GENRE (e.g., "hip hop songs", "rock music", "pop tracks"), ALWAYS use "fetch_and_store_tracks_by_genre" tool** - even if they mention "charts" or "popular". This will get you genre-specific songs.
- **ONLY use "fetch_and_store_chart_tracks" when the user asks for general/popular songs WITHOUT specifying a genre** (e.g., "what's popular", "top charts", "popular songs").
- If the user asks for ARTISTS in a genre, use "fetch_and_store_artists_by_genre" tool.
- If a tool returns an error (check for "error": true in the result), explain the issue to the user and suggest alternatives (e.g., try a different genre, or use the chart tracks tool).
- **When presenting tracks/songs, ALWAYS use the actual "title" and "artist" values from the tool result. Do NOT use placeholder text like "[Artist Name 1]" or "[Song Title 1]".**
- Present tool results in a simple, user-friendly format (e.g., "Here are some [genre] songs: [actual song title] by [actual artist name], [actual song title] by [actual artist name]...")
- Be concise and direct - no long explanations."""

def chat_with_ai(messages_history: list) -> dict:
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
    
    api_key_clean = api_key.strip()
    if len(api_key_clean) > 14:
        key_preview = f"{api_key_clean[:10]}...{api_key_clean[-4:]}"
    else:
        key_preview = "***"  # Too short to preview safely
    print(f"[DEBUG] Using API key: {key_preview} (length: {len(api_key_clean)})")
    
    # Check API key format (OpenRouter keys typically start with sk-or-v1- or sk-or-v2-)
    if not api_key_clean.startswith('sk-or-'):
        print(f"[WARNING] API key doesn't start with 'sk-or-'. It starts with: {api_key_clean[:10]}...")
        # Don't fail here - some keys might have different formats
    
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
    
    # Prepare the request payload
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            }
        ] + messages_history, 
        "tools": tools,          
        "tool_choice": "auto"    
    }
    
    fallback_models = [
        'microsoft/phi-3-mini-128k-instruct:free',  # Fast and reliable alternative
        'google/gemini-flash-1.5-8b:free',  # Generally available, fast response
        'deepseek/deepseek-chat-v3.1:free',  # Good performance and quality
        'qwen/qwen-2-7b-instruct:free',  # Reliable alternative with good reasoning
        'google/gemini-2.0-flash-exp:free',  # Latest Gemini model when available
        'meta-llama/llama-3.1-8b-instruct:free',  # Alternative Llama model
    ]
    

    # Remove the primary model from fallback list if it's already there
    if model in fallback_models:
        fallback_models = [m for m in fallback_models if m != model]
    
    models_to_try = [model] + fallback_models
    last_error = None
    
    print(f"[DEBUG] Will try {len(models_to_try)} models: {', '.join(models_to_try)}")
    
    # Try each model until one works
    for idx, attempt_model in enumerate(models_to_try, 1):
        print(f"[DEBUG] Attempt {idx}/{len(models_to_try)}: Trying model '{attempt_model}'...")
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
                
                # Check for authentication/authorization errors first
                error_lower = error_message.lower()
                is_auth_error = (
                    'user not found' in error_lower or
                    'authentication' in error_lower or
                    'unauthorized' in error_lower or
                    'invalid api key' in error_lower or
                    'api key' in error_lower and ('invalid' in error_lower or 'missing' in error_lower)
                )
                
                if is_auth_error:
                    raise Exception(
                        f"Authentication error: {error_message}\n\n"
                        "This usually means:\n"
                        "1. Your API key is invalid or expired\n"
                        "2. Your API key doesn't have access to this model\n"
                        "3. Your OpenRouter account needs credits\n\n"
                        "Please check your OPEN_AI_API key at https://openrouter.ai/keys"
                    )
                
                # Check for specific error types that indicate model unavailability
                is_model_unavailable = (
                    'provider' in error_type.lower() or 
                    'provider' in error_message.lower() or
                    'provider returned error' in error_lower or
                    'no endpoints' in error_lower or
                    'endpoint not found' in error_lower or
                    'model not found' in error_lower or
                    'unavailable' in error_lower or
                    'at capacity' in error_lower or
                    'rate limit' in error_lower
                )
                
                # If it's a model availability error, try next model
                if is_model_unavailable:
                    print(f"[DEBUG] Model '{attempt_model}' unavailable: {error_message}, trying next...")
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
                # Get the entire message object from the AI
                message = result['choices'][0]['message'] 
                
                # Check if it has content OR a tool call
                if message.get("content") or message.get("tool_calls"):
                    print(f"[DEBUG] Success! Model '{attempt_model}' responded successfully.")
                    return message # <-- Return the FULL message object (a dict)
                
                last_error = f"Model {attempt_model} returned empty/invalid message"
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
        "5. Try setting OPENROUTER_MODEL in .env to a specific model, for example:\n"
        "   OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free\n"
        "   or\n"
        "   OPENROUTER_MODEL=microsoft/phi-3-mini-128k-instruct:free"
    )
