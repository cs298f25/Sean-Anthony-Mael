"""
Tests for weather.py - functions that interact with Google Maps and Weather APIs.
We'll use mocking to avoid making real API calls during tests.
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set required API keys in environment before importing weather module
os.environ['GOOGLE_MAPS_KEY'] = 'test_google_maps_key'
os.environ['WEATHER_API'] = 'test_weather_api_key'

# Now import weather (it will check for API keys)
import weather

def test_get_longitude_latitude_success():
    """
    Test: Can we get longitude and latitude when API call succeeds?
    
    This test checks that:
    - The function makes the correct API call
    - Parses the response correctly
    - Returns latitude and longitude as a tuple
    """
    # Step 1: Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'location': {
            'lat': 40.7128,
            'lng': -74.0060
        }
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post to return our mock response
    with patch('weather.requests.post', return_value=mock_response):
        # Step 3: Call the function
        latitude, longitude = weather.get_longitude_latitude()
    
    # Step 4: Verify the result
    assert latitude == 40.7128, "Latitude should match"
    assert longitude == -74.0060, "Longitude should match"
    assert isinstance(latitude, float), "Latitude should be a float"
    assert isinstance(longitude, float), "Longitude should be a float"

def test_get_longitude_latitude_missing_api_key():
    """
    Test: What happens when GOOGLE_MAPS_KEY is missing?
    
    This test checks that:
    - The function raises RuntimeError when API key is missing
    """
    # Step 1: Mock os.getenv to return None (simulating missing key)
    with patch('weather.os.getenv', return_value=None):
        # Step 2: Call should raise RuntimeError
        with pytest.raises(RuntimeError, match='Missing GOOGLE_MAPS_KEY'):
            weather.get_longitude_latitude()

def test_get_longitude_latitude_missing_location():
    """
    Test: What happens when API response is missing location data?
    
    This test checks that:
    - The function raises RuntimeError when location data is missing
    """
    # Step 1: Mock the API response without location
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'location': {}  # Empty location dict
    }
    mock_response.raise_for_status = MagicMock()
    
    # Step 2: Mock requests.post
    with patch('weather.requests.post', return_value=mock_response):
        # Step 3: Call should raise RuntimeError
        with pytest.raises(RuntimeError, match='Failed to get location'):
            weather.get_longitude_latitude()

def test_get_longitude_latitude_api_failure():
    """
    Test: What happens when the API call fails?
    
    This test checks that:
    - The function raises an exception when API fails
    """
    # Step 1: Mock requests.post to raise an exception
    with patch('weather.requests.post', side_effect=Exception("API Error")):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception):
            weather.get_longitude_latitude()

def test_build_weather_url_success():
    """
    Test: Can we build a weather URL when location API succeeds?
    
    This test checks that:
    - The function calls get_longitude_latitude()
    - Builds the correct URL with latitude, longitude, and API key
    """
    # Step 1: Mock get_longitude_latitude to return test coordinates
    with patch('weather.get_longitude_latitude', return_value=(40.7128, -74.0060)):
        # Step 2: Call the function
        url = weather.build_weather_url()
    
    # Step 3: Verify the URL
    assert isinstance(url, str), "Should return a string"
    assert 'api.weatherapi.com' in url, "Should contain weather API domain"
    assert 'test_weather_api_key' in url, "Should contain API key"
    assert '40.7128' in url, "Should contain latitude"
    assert '-74.006' in url, "Should contain longitude (Python removes trailing zeros)"
    assert 'current.json' in url, "Should contain current.json endpoint"

def test_build_weather_url_missing_api_key():
    """
    Test: What happens when WEATHER_API key is missing?
    
    This test checks that:
    - The function raises RuntimeError when API key is missing
    """
    # Step 1: Mock get_longitude_latitude to succeed
    # Step 2: Mock os.getenv to return None for WEATHER_API
    with patch('weather.get_longitude_latitude', return_value=(40.7128, -74.0060)), \
         patch('weather.os.getenv', side_effect=lambda key, default=None: None if key == 'WEATHER_API' else os.environ.get(key, default)):
        # Step 3: Call should raise RuntimeError
        with pytest.raises(RuntimeError, match='Missing WEATHER_API'):
            weather.build_weather_url()

def test_build_astronomy_url_success():
    """
    Test: Can we build an astronomy URL when location API succeeds?
    
    This test checks that:
    - The function calls get_longitude_latitude()
    - Builds the correct URL with latitude, longitude, and API key
    """
    # Step 1: Mock get_longitude_latitude to return test coordinates
    with patch('weather.get_longitude_latitude', return_value=(34.0522, -118.2437)):
        # Step 2: Call the function
        url = weather.build_astronomy_url()
    
    # Step 3: Verify the URL
    assert isinstance(url, str), "Should return a string"
    assert 'api.weatherapi.com' in url, "Should contain weather API domain"
    assert 'test_weather_api_key' in url, "Should contain API key"
    assert '34.0522' in url, "Should contain latitude"
    assert '-118.2437' in url, "Should contain longitude"
    assert 'astronomy.json' in url, "Should contain astronomy.json endpoint"

def test_build_astronomy_url_missing_api_key():
    """
    Test: What happens when WEATHER_API key is missing for astronomy URL?
    
    This test checks that:
    - The function raises RuntimeError when API key is missing
    """
    # Step 1: Mock get_longitude_latitude to succeed
    # Step 2: Mock os.getenv to return None for WEATHER_API
    with patch('weather.get_longitude_latitude', return_value=(40.7128, -74.0060)), \
         patch('weather.os.getenv', side_effect=lambda key, default=None: None if key == 'WEATHER_API' else os.environ.get(key, default)):
        # Step 3: Call should raise RuntimeError
        with pytest.raises(RuntimeError, match='Missing WEATHER_API'):
            weather.build_astronomy_url()

def test_fetch_weather_success():
    """
    Test: Can we fetch weather data when all API calls succeed?
    
    This test checks that:
    - The function calls build_weather_url() and build_astronomy_url()
    - Makes API calls to both endpoints
    - Parses and combines the responses correctly
    - Returns a dictionary with all required fields
    """
    # Step 1: Mock the weather API response
    mock_weather_response = MagicMock()
    mock_weather_response.json.return_value = {
        'location': {
            'name': 'New York',
            'region': 'New York',
            'country': 'United States of America'
        },
        'current': {
            'temp_f': 72.5,
            'feelslike_f': 70.0,
            'condition': {
                'text': 'Sunny'
            },
            'last_updated': '2024-01-01 12:00'
        }
    }
    mock_weather_response.raise_for_status = MagicMock()
    
    # Step 2: Mock the astronomy API response
    mock_astronomy_response = MagicMock()
    mock_astronomy_response.json.return_value = {
        'astronomy': {
            'astro': {
                'sunrise': '6:30 AM',
                'sunset': '7:45 PM'
            }
        }
    }
    mock_astronomy_response.raise_for_status = MagicMock()
    
    # Step 3: Mock get requests to return different responses for different URLs
    def mock_get(url, **kwargs):
        if 'astronomy' in url:
            return mock_astronomy_response
        return mock_weather_response
    
    # Step 4: Mock build_weather_url and build_astronomy_url
    with patch('weather.build_weather_url', return_value='http://weather.api/current.json'), \
         patch('weather.build_astronomy_url', return_value='http://weather.api/astronomy.json'), \
         patch('weather.requests.get', side_effect=mock_get):
        # Step 5: Call the function
        result = weather.fetch_weather()
    
    # Step 6: Verify the result structure
    assert isinstance(result, dict), "Should return a dictionary"
    assert result['city'] == 'New York', "City should match"
    assert result['region'] == 'New York', "Region should match"
    assert result['country'] == 'United States of America', "Country should match"
    assert result['temperature_f'] == 72.5, "Temperature should match"
    assert result['feels_like_f'] == 70.0, "Feels like temperature should match"
    assert result['condition_text'] == 'Sunny', "Condition should match"
    assert result['last_updated'] == '2024-01-01 12:00', "Last updated should match"
    assert result['sunrise'] == '6:30 AM', "Sunrise should match"
    assert result['sunset'] == '7:45 PM', "Sunset should match"

def test_fetch_weather_weather_api_failure():
    """
    Test: What happens when the weather API call fails?
    
    This test checks that:
    - The function raises an exception when weather API fails
    """
    # Step 1: Mock build functions
    with patch('weather.build_weather_url', return_value='http://weather.api/current.json'), \
         patch('weather.build_astronomy_url', return_value='http://weather.api/astronomy.json'), \
         patch('weather.requests.get', side_effect=Exception("Weather API Error")):
        # Step 2: Call should raise an exception
        with pytest.raises(Exception):
            weather.fetch_weather()

def test_fetch_weather_astronomy_api_failure():
    """
    Test: What happens when the astronomy API call fails?
    
    This test checks that:
    - The function raises an exception when astronomy API fails
    """
    # Step 1: Mock weather API to succeed, astronomy to fail
    mock_weather_response = MagicMock()
    mock_weather_response.json.return_value = {
        'location': {'name': 'Test City'},
        'current': {'temp_f': 70, 'feelslike_f': 68, 'condition': {'text': 'Clear'}, 'last_updated': '2024-01-01'}
    }
    mock_weather_response.raise_for_status = MagicMock()
    
    def mock_get(url, **kwargs):
        if 'astronomy' in url:
            raise Exception("Astronomy API Error")
        return mock_weather_response
    
    # Step 2: Mock build functions
    with patch('weather.build_weather_url', return_value='http://weather.api/current.json'), \
         patch('weather.build_astronomy_url', return_value='http://weather.api/astronomy.json'), \
         patch('weather.requests.get', side_effect=mock_get):
        # Step 3: Call should raise an exception
        with pytest.raises(Exception):
            weather.fetch_weather()

