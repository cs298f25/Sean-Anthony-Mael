"""
Tests for music.py - functions that interact with the Last.fm API.
We'll use mocking to avoid making real API calls during tests.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set MUSIC_KEY in environment before importing music module
# This prevents the ValueError from being raised during import
os.environ['MUSIC_KEY'] = 'test_api_key'

# Now import music (it will check for MUSIC_KEY)
import music

def test_get_top_genres_success():
    """
    Test: Can we get top genres when API call succeeds?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns a list of genre names
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'toptags': {
            'tag': [
                {'name': 'rock'},
                {'name': 'pop'},
                {'name': 'jazz'}
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get to return our mock response
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_top_genres()
    
    # Step 4: Verify the result
    assert isinstance(result, list), "Should return a list"
    assert len(result) == 3, "Should return 3 genres"
    assert 'rock' in result, "Should contain 'rock'"
    assert 'pop' in result, "Should contain 'pop'"
    assert 'jazz' in result, "Should contain 'jazz'"

def test_get_top_genres_api_failure():
    """
    Test: What happens when the API call fails?
    
    This test checks that:
    - The function raises an exception when API fails
    - Error handling works correctly
    """
    # Step 1: Mock requests.get to raise an exception
    with patch('src.music.requests.get', side_effect=Exception("API Error")):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception):
            music.get_top_genres()

def test_get_top_artists_by_genre_success():
    """
    Test: Can we get top artists by genre when API call succeeds?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns a list of artist names
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'artists': {
            'artist': [
                {'name': 'Artist 1'},
                {'name': 'Artist 2'},
                {'name': 'Artist 3'}
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_top_artists_by_genre('rock')
    
    # Step 4: Verify the result
    assert isinstance(result, list), "Should return a list"
    assert len(result) == 3, "Should return 3 artists"
    assert 'Artist 1' in result, "Should contain 'Artist 1'"
    assert 'Artist 2' in result, "Should contain 'Artist 2'"

def test_get_top_artists_by_genre_single_artist():
    """
    Test: Can we handle when API returns a single artist (dict) instead of a list?
    
    This test checks that:
    - The function handles the edge case where API returns one artist as a dict
    - Converts it to a list correctly
    """
    # Step 1: Mock the API response with single artist (dict, not list)
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'artists': {
            'artist': {'name': 'Single Artist'}  # Single dict, not a list
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_top_artists_by_genre('rock')
    
    # Step 4: Verify the result
    assert isinstance(result, list), "Should return a list"
    assert len(result) == 1, "Should return 1 artist"
    assert 'Single Artist' in result, "Should contain 'Single Artist'"

def test_get_top_artists_by_genre_api_error():
    """
    Test: What happens when API returns an error response?
    
    This test checks that:
    - The function handles API error responses gracefully
    - Returns an empty list
    """
    # Step 1: Mock the API response with error
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'error': 6,
        'message': 'Invalid parameters'
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_top_artists_by_genre('invalid')
    
    # Step 4: Should return empty list
    assert result == [], "Should return empty list on API error"

def test_get_top_artists_by_genre_missing_artists_key():
    """
    Test: What happens when API response is missing 'artists' key?
    
    This test checks that:
    - The function handles malformed API responses
    - Returns an empty list
    """
    # Step 1: Mock the API response missing 'artists' key
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'something': 'else'
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_top_artists_by_genre('rock')
    
    # Step 4: Should return empty list
    assert result == [], "Should return empty list when 'artists' key is missing"

def test_get_top_artists_by_genre_request_exception():
    """
    Test: What happens when the HTTP request fails?
    
    This test checks that:
    - The function handles network/request errors gracefully
    - Returns an empty list
    """
    # Step 1: Mock requests.get to raise RequestException
    import requests
    with patch('src.music.requests.get', side_effect=requests.exceptions.RequestException("Network error")):
        # Step 2: Call the function
        result = music.get_top_artists_by_genre('rock')
    
    # Step 3: Should return empty list
    assert result == [], "Should return empty list on request exception"

def test_get_artist_info_success():
    """
    Test: Can we get artist info when API call succeeds?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns artist info with name, bio, and genres
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'artist': {
            'name': 'Test Artist',
            'bio': {
                'summary': 'This is a test artist bio'
            },
            'genres': {
                'genre': [
                    {'name': 'rock'},
                    {'name': 'alternative'}
                ]
            }
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_artist_info('Test Artist')
    
    # Step 4: Verify the result
    assert isinstance(result, dict), "Should return a dictionary"
    assert result['name'] == 'Test Artist', "Name should match"
    assert result['bio'] == 'This is a test artist bio', "Bio should match"
    assert 'rock' in [g['name'] for g in result['genres']], "Should contain 'rock' genre"

def test_get_artist_top_tracks_success():
    """
    Test: Can we get artist top tracks when API call succeeds?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns a list of track dictionaries with name, artist, and duration
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'tracks': {
            'track': [
                {'name': 'Track 1', 'duration': 180},
                {'name': 'Track 2', 'duration': 200}
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_artist_top_tracks('Test Artist')
    
    # Step 4: Verify the result
    assert isinstance(result, list), "Should return a list"
    assert len(result) == 2, "Should return 2 tracks"
    assert result[0]['name'] == 'Track 1', "First track name should match"
    assert result[0]['artist'] == 'Test Artist', "Artist should match input"
    assert result[0]['duration'] == 180, "Duration should match"
    assert isinstance(result[0]['duration'], int), "Duration should be an integer"

def test_get_artist_top_tracks_missing_duration():
    """
    Test: Can we handle tracks with missing duration field?
    
    This test checks that:
    - The function handles missing duration gracefully
    - Defaults to 0 when duration is missing
    """
    # Step 1: Mock the API response with missing duration
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'tracks': {
            'track': [
                {'name': 'Track Without Duration'}  # No duration field
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_artist_top_tracks('Test Artist')
    
    # Step 4: Verify duration defaults to 0
    assert result[0]['duration'] == 0, "Duration should default to 0 when missing"

def test_get_chart_top_tracks_success():
    """
    Test: Can we get chart top tracks when API call succeeds?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns a list of track dictionaries
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'tracks': {
            'track': [
                {
                    'name': 'Chart Track 1',
                    'artist': {'name': 'Chart Artist 1'},
                    'duration': 180
                },
                {
                    'name': 'Chart Track 2',
                    'artist': {'name': 'Chart Artist 2'},
                    'duration': 200
                }
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_chart_top_tracks()
    
    # Step 4: Verify the result
    assert isinstance(result, list), "Should return a list"
    assert len(result) == 2, "Should return 2 tracks"
    assert result[0]['name'] == 'Chart Track 1', "Track name should match"
    assert result[0]['artist'] == 'Chart Artist 1', "Artist name should match"
    assert result[0]['duration'] == 180, "Duration should match"

def test_get_similar_artists_success():
    """
    Test: Can we get similar artists when API call succeeds?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns a list of artist names
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'similarartists': {
            'artist': [
                {'name': 'Similar Artist 1'},
                {'name': 'Similar Artist 2'},
                {'name': 'Similar Artist 3'}
            ]
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.get
    with patch('src.music.requests.get', return_value=mock_response):
        # Step 3: Call the function
        result = music.get_similar_artists('Original Artist')
    
    # Step 4: Verify the result
    assert isinstance(result, list), "Should return a list"
    assert len(result) == 3, "Should return 3 artists"
    assert 'Similar Artist 1' in result, "Should contain 'Similar Artist 1'"
    assert 'Similar Artist 2' in result, "Should contain 'Similar Artist 2'"
    assert 'Similar Artist 3' in result, "Should contain 'Similar Artist 3'"

def test_get_artist_info_api_failure():
    """
    Test: What happens when get_artist_info API call fails?
    
    This test checks that:
    - The function raises an exception when API fails
    """
    # Step 1: Mock requests.get to raise an exception
    with patch('src.music.requests.get', side_effect=Exception("API Error")):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception):
            music.get_artist_info('Test Artist')

def test_get_artist_top_tracks_api_failure():
    """
    Test: What happens when get_artist_top_tracks API call fails?
    
    This test checks that:
    - The function raises an exception when API fails
    """
    # Step 1: Mock requests.get to raise an exception
    with patch('src.music.requests.get', side_effect=Exception("API Error")):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception):
            music.get_artist_top_tracks('Test Artist')

def test_get_chart_top_tracks_api_failure():
    """
    Test: What happens when get_chart_top_tracks API call fails?
    
    This test checks that:
    - The function raises an exception when API fails
    """
    # Step 1: Mock requests.get to raise an exception
    with patch('src.music.requests.get', side_effect=Exception("API Error")):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception):
            music.get_chart_top_tracks()

def test_get_similar_artists_api_failure():
    """
    Test: What happens when get_similar_artists API call fails?
    
    This test checks that:
    - The function raises an exception when API fails
    """
    # Step 1: Mock requests.get to raise an exception
    with patch('src.music.requests.get', side_effect=Exception("API Error")):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception):
            music.get_similar_artists('Test Artist')

