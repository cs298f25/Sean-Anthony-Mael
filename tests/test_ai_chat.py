"""
Tests for ai_chat.py - functions that interact with OpenRouter AI API.
We'll use mocking to avoid making real API calls during tests.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
import requests

# Add src directory to path (ai_chat.py is in src/)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set required API key in environment before importing ai_chat module
os.environ['OPEN_AI_API'] = 'sk-or-v1-test-api-key-1234567890'

# Now import ai_chat (it will check for API key)
import ai_chat

def test_chat_with_ai_success_with_content():
    """
    Test: Can we get a successful AI response with content?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns the message object with content
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': 'Hello! How can I help you today?'
            }
        }]
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post to return our mock response
    with patch('ai_chat.requests.post', return_value=mock_response), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 3: Call the function
        messages = [{'role': 'user', 'content': 'Hello'}]
        result = ai_chat.chat_with_ai(messages)
    
    # Step 4: Verify the result
    assert isinstance(result, dict), "Should return a dictionary"
    assert result['role'] == 'assistant', "Should have assistant role"
    assert result['content'] == 'Hello! How can I help you today?', "Content should match"
    assert 'content' in result, "Should have content field"

def test_chat_with_ai_success_with_tool_calls():
    """
    Test: Can we get a successful AI response with tool calls?
    
    This test checks that:
    - The function handles tool calls in the response
    - Returns the message object with tool_calls
    """
    # Step 1: Mock the API response with tool calls
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'tool_calls': [{
                    'id': 'call_123',
                    'type': 'function',
                    'function': {
                        'name': 'fetch_and_store_tracks_by_genre',
                        'arguments': '{"genre": "rock"}'
                    }
                }]
            }
        }]
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post
    with patch('ai_chat.requests.post', return_value=mock_response), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 3: Call the function
        messages = [{'role': 'user', 'content': 'Get me some rock songs'}]
        result = ai_chat.chat_with_ai(messages)
    
    # Step 4: Verify the result
    assert isinstance(result, dict), "Should return a dictionary"
    assert result['role'] == 'assistant', "Should have assistant role"
    assert 'tool_calls' in result, "Should have tool_calls field"
    assert len(result['tool_calls']) == 1, "Should have one tool call"
    assert result['tool_calls'][0]['function']['name'] == 'fetch_and_store_tracks_by_genre', "Tool call name should match"

def test_chat_with_ai_missing_api_key():
    """
    Test: What happens when OPEN_AI_API key is missing?
    
    This test checks that:
    - The function raises an exception when API key is missing
    """
    # Step 1: Mock os.getenv to return None for OPEN_AI_API
    with patch('ai_chat.api_key', None):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception, match='OPEN_AI_API key is not set'):
            messages = [{'role': 'user', 'content': 'Hello'}]
            ai_chat.chat_with_ai(messages)

def test_chat_with_ai_empty_api_key():
    """
    Test: What happens when OPEN_AI_API key is empty?
    
    This test checks that:
    - The function raises an exception when API key is empty
    """
    # Step 1: Mock api_key to be empty string
    with patch('ai_chat.api_key', ''):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception, match='OPEN_AI_API key is not set'):
            messages = [{'role': 'user', 'content': 'Hello'}]
            ai_chat.chat_with_ai(messages)

def test_chat_with_ai_authentication_error():
    """
    Test: What happens when API returns authentication error?
    
    This test checks that:
    - The function raises an exception with helpful message for auth errors
    - Does not try fallback models for auth errors
    """
    # Step 1: Mock the API response with authentication error
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.json.return_value = {
        'error': {
            'message': 'Invalid API key',
            'type': 'authentication_error'
        }
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
    
    # Step 2: Mock requests.post
    with patch('ai_chat.requests.post', return_value=mock_response), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 3: Call should raise an exception
        with pytest.raises(Exception, match='Authentication'):
            messages = [{'role': 'user', 'content': 'Hello'}]
            ai_chat.chat_with_ai(messages)

def test_chat_with_ai_model_unavailable_fallback():
    """
    Test: Does the function try fallback models when primary model is unavailable?
    
    This test checks that:
    - The function tries the primary model first
    - Falls back to next model when primary model is unavailable
    - Returns success when fallback model works
    """
    # Step 1: Create mock responses - first model fails, second succeeds
    mock_response_fail = MagicMock()
    mock_response_fail.status_code = 200
    mock_response_fail.json.return_value = {
        'error': {
            'message': 'Model unavailable',
            'type': 'provider_error'
        }
    }
    
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': 'Success from fallback model!'
            }
        }]
    }
    mock_response_success.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post to return different responses
    call_count = 0
    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_response_fail
        return mock_response_success
    
    # Step 3: Mock requests.post
    with patch('ai_chat.requests.post', side_effect=mock_post), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 4: Call the function
        messages = [{'role': 'user', 'content': 'Hello'}]
        result = ai_chat.chat_with_ai(messages)
    
    # Step 5: Verify the result
    assert result['content'] == 'Success from fallback model!', "Should get response from fallback model"
    assert call_count == 2, "Should have tried 2 models"

def test_chat_with_ai_all_models_fail():
    """
    Test: What happens when all models fail?
    
    This test checks that:
    - The function tries all models
    - Raises an exception when all models fail
    """
    # Step 1: Mock the API response with model unavailable error
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'error': {
            'message': 'Model unavailable',
            'type': 'provider_error'
        }
    }
    
    # Step 2: Mock requests.post to always return the error
    with patch('ai_chat.requests.post', return_value=mock_response), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 3: Call should raise an exception
        with pytest.raises(Exception, match='All AI models failed'):
            messages = [{'role': 'user', 'content': 'Hello'}]
            ai_chat.chat_with_ai(messages)

def test_chat_with_ai_network_error_fallback():
    """
    Test: Does the function try fallback models on network errors?
    
    This test checks that:
    - The function handles network errors
    - Tries next model on network errors
    """
    # Step 1: Create mock responses - first fails with network error, second succeeds
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': 'Success after network error!'
            }
        }]
    }
    mock_response_success.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post - first call raises network error, second succeeds
    call_count = 0
    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise requests.exceptions.RequestException("Network error")
        return mock_response_success
    
    # Step 3: Mock requests.post
    with patch('ai_chat.requests.post', side_effect=mock_post), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 4: Call the function
        messages = [{'role': 'user', 'content': 'Hello'}]
        result = ai_chat.chat_with_ai(messages)
    
    # Step 5: Verify the result
    assert result['content'] == 'Success after network error!', "Should get response after network error"
    assert call_count == 2, "Should have tried 2 models"

def test_chat_with_ai_invalid_json_response():
    """
    Test: What happens when API returns invalid JSON?
    
    This test checks that:
    - The function handles invalid JSON responses
    - Raises an appropriate exception
    """
    # Step 1: Mock the API response with invalid JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post
    with patch('ai_chat.requests.post', return_value=mock_response), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 3: Call should raise an exception
        with pytest.raises(Exception, match='Invalid JSON'):
            messages = [{'role': 'user', 'content': 'Hello'}]
            ai_chat.chat_with_ai(messages)

def test_chat_with_ai_empty_choices():
    """
    Test: What happens when API returns empty choices?
    
    This test checks that:
    - The function handles empty choices array
    - Tries next model when response is invalid
    """
    # Step 1: Create mock responses - first has empty choices, second succeeds
    mock_response_empty = MagicMock()
    mock_response_empty.status_code = 200
    mock_response_empty.json.return_value = {
        'choices': []
    }
    mock_response_empty.raise_for_status = MagicMock()
    
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': 'Success!'
            }
        }]
    }
    mock_response_success.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post
    call_count = 0
    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_response_empty
        return mock_response_success
    
    # Step 3: Mock requests.post
    with patch('ai_chat.requests.post', side_effect=mock_post), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 4: Call the function
        messages = [{'role': 'user', 'content': 'Hello'}]
        result = ai_chat.chat_with_ai(messages)
    
    # Step 5: Verify the result
    assert result['content'] == 'Success!', "Should get response from fallback model"
    assert call_count == 2, "Should have tried 2 models"

def test_chat_with_ai_message_without_content_or_tool_calls():
    """
    Test: What happens when message has neither content nor tool_calls?
    
    This test checks that:
    - The function handles messages without content or tool_calls
    - Tries next model when response is invalid
    """
    # Step 1: Create mock responses - first has no content/tool_calls, second succeeds
    mock_response_invalid = MagicMock()
    mock_response_invalid.status_code = 200
    mock_response_invalid.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant'
                # No content or tool_calls
            }
        }]
    }
    mock_response_invalid.raise_for_status = MagicMock()
    
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': 'Success!'
            }
        }]
    }
    mock_response_success.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post
    call_count = 0
    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_response_invalid
        return mock_response_success
    
    # Step 3: Mock requests.post
    with patch('ai_chat.requests.post', side_effect=mock_post), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 4: Call the function
        messages = [{'role': 'user', 'content': 'Hello'}]
        result = ai_chat.chat_with_ai(messages)
    
    # Step 5: Verify the result
    assert result['content'] == 'Success!', "Should get response from fallback model"
    assert call_count == 2, "Should have tried 2 models"

def test_chat_with_ai_http_error_non_401():
    """
    Test: What happens when API returns HTTP error (not 401)?
    
    This test checks that:
    - The function handles non-401 HTTP errors
    - Tries next model on HTTP errors
    """
    # Step 1: Create mock responses - first fails with HTTP error, second succeeds
    mock_response_error = MagicMock()
    mock_response_error.status_code = 500
    mock_response_error.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response_error)
    
    mock_response_success = MagicMock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {
        'choices': [{
            'message': {
                'role': 'assistant',
                'content': 'Success after HTTP error!'
            }
        }]
    }
    mock_response_success.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post
    call_count = 0
    def mock_post(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_response_error
        return mock_response_success
    
    # Step 3: Mock requests.post
    with patch('ai_chat.requests.post', side_effect=mock_post), \
         patch('ai_chat.os.getenv', side_effect=lambda key, default=None: {
             'OPEN_AI_API': 'sk-or-v1-test-key',
             'OPENROUTER_MODEL': 'meta-llama/llama-3.2-3b-instruct:free',
             'OPENROUTER_REFERER': 'http://localhost:8000',
             'OPENROUTER_TITLE': 'Zen Study Assistant'
         }.get(key, default)):
        # Step 4: Call the function
        messages = [{'role': 'user', 'content': 'Hello'}]
        result = ai_chat.chat_with_ai(messages)
    
    # Step 5: Verify the result
    assert result['content'] == 'Success after HTTP error!', "Should get response after HTTP error"
    assert call_count == 2, "Should have tried 2 models"

