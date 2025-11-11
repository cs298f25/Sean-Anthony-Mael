import json
import sys
from pathlib import Path
import traceback

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import ai_chat 
from database import services

# --- 1. Tool Dispatcher ---
# This maps the tool name (from the AI) to the actual Python function
AVAILABLE_TOOLS = {
    "fetch_and_store_artists_by_genre": services.fetch_and_store_artists_by_genre,
    "fetch_and_store_tracks_by_genre": services.fetch_and_store_tracks_by_genre,
    "get_and_store_tracks_for_artist_by_name": services.get_and_store_tracks_for_artist_by_name,
    "fetch_and_store_chart_tracks": services.fetch_and_store_chart_tracks,
    "fetch_and_store_similar_artists": services.fetch_and_store_similar_artists,
}

def format_track_results_for_ai(tool_result):
    """
    Formats track results in a clear, explicit way for the AI to understand.
    This helps prevent the AI from using placeholder text.
    """
    if not tool_result:
        return tool_result
    
    # If it's a list of tracks, format each one clearly
    if isinstance(tool_result, list) and len(tool_result) > 0:
        # Check if it's a list of track dictionaries
        if isinstance(tool_result[0], dict):
            # Format tracks with explicit labels
            formatted = []
            for track in tool_result:
                # Handle different possible field names
                title = track.get('title') or track.get('name') or track.get('track_title', 'Unknown Track')
                artist = track.get('artist') or track.get('artist_name', 'Unknown Artist')
                
                formatted.append({
                    'song_title': title,
                    'artist_name': artist,
                    'title': title,  # Keep original for compatibility
                    'artist': artist  # Keep original for compatibility
                })
            return formatted
    
    return tool_result

def handle_chat_message(user_message: str, messages_history: list) -> (str, list):
    """
    Handles a single user message, running the full AI tool-use loop.
    """
    
    # 1. Add the new user message to the conversation history
    messages_history.append({"role": "user", "content": user_message})
    
    try:
        # 2. Get the AI's first response
        ai_message = ai_chat.chat_with_ai(messages_history)
        
        # 3. Add the AI's (potentially complex) response to the history
        messages_history.append(ai_message)
        
        # 4. Check if the AI wants to use a tool
        if ai_message.get("tool_calls"):
            
            tool_call = ai_message["tool_calls"][0]
            tool_name = tool_call['function']['name']
            
            if tool_name in AVAILABLE_TOOLS:
                tool_function = AVAILABLE_TOOLS[tool_name]
                
                # Parse the arguments the AI wants to use
                try:
                    args_data = tool_call['function'].get('arguments', '{}')
                    # Handle case where arguments might already be a dict
                    if isinstance(args_data, dict):
                        tool_args = args_data
                    else:
                        # Try to parse as JSON string
                        if not args_data or not args_data.strip():
                            args_data = '{}'
                        tool_args = json.loads(args_data)
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"[ERROR] Failed to parse tool arguments: {e}")
                    print(f"[DEBUG] Arguments data: {tool_call['function'].get('arguments', 'N/A')}")
                    return f"Error: Could not parse tool arguments. Please try rephrasing your request.", messages_history
                                
                # Call the tool function
                try:
                    tool_result = tool_function(**tool_args)
                except Exception as e:
                    print(f"[ERROR] Tool {tool_name} failed: {e}")
                    traceback.print_exc()
                    tool_result = {"error": str(e), "message": f"Failed to fetch data: {e}"}
                
                # Format track results for better AI understanding
                if tool_name in ["fetch_and_store_chart_tracks", "fetch_and_store_tracks_by_genre", "get_and_store_tracks_for_artist_by_name"]:
                    tool_result = format_track_results_for_ai(tool_result)
                
                # Serialize tool result to JSON
                try:
                    # Handle None, lists, dicts, etc.
                    if tool_result is None:
                        result_content = "null"
                    else:
                        result_content = json.dumps(tool_result, default=str)  # default=str handles non-serializable objects
                except (TypeError, ValueError) as e:
                    print(f"[ERROR] Failed to serialize tool result: {e}")
                    print(f"[DEBUG] Tool result type: {type(tool_result)}")
                    result_content = json.dumps({"error": "Failed to format results", "raw": str(tool_result)})
                
                # 7. Send the tool's result back to the AI
                messages_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call['id'],
                    "name": tool_name,
                    "content": result_content, 
                })
                
                # 8. Get the AI's *final* response (now that it has the data)
                final_ai_message = ai_chat.chat_with_ai(messages_history)
                messages_history.append(final_ai_message)
                
                # Return the final text content
                return final_ai_message['content'], messages_history
                
            else:
                # AI tried to call a tool that doesn't exist
                return f"Error: AI tried to call an unknown tool: {tool_name}", messages_history

        # 4b. If no tool call, just return the simple text response
        elif ai_message.get("content"):
            return ai_message['content'], messages_history
            
        else:
            return "Error: AI returned an invalid response.", messages_history
            
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"--- CHAT CONTROLLER ERROR: {e} ---")
        print(f"Full traceback:\n{error_details}")
        # Return a user-friendly error with more details in development
        error_msg = f"Sorry, an error occurred while processing your request: {str(e)}"
        return error_msg, messages_history

if __name__ == "__main__":
    """
    This block lets you test the controller directly from your terminal.
    It simulates a chat session by keeping the history in memory.
    """
    conversation_history = [] 
    
    print("🤖 Zen: Hi! I'm Zen. Ask me for study tips or music recommendations.")
    print(" (Type 'exit' to quit)")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # Get the response and the updated history
        final_response, updated_history = handle_chat_message(
            user_input, 
            conversation_history
        )
        
        print(f"Zen: {final_response}")
        
        conversation_history = updated_history