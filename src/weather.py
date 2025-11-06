from dotenv import load_dotenv
import os
import requests

def get_longitude_latitude():
    api_key = os.getenv('GOOGLE_MAPS_KEY')
    if not api_key:
        raise RuntimeError('Missing GOOGLE_MAPS_KEY in environment')
    
    url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"
    # Make POST request with empty body (API uses device's network info)
    response = requests.post(url, json={}, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    # Extract latitude and longitude from response
    location = data.get('location', {})
    latitude = location.get('lat')
    longitude = location.get('lng')
    
    if latitude is None or longitude is None:
        raise RuntimeError('Failed to get location from geolocation API')
    
    return latitude, longitude


def build_weather_url():
    lat, lon = get_longitude_latitude()
    api_key = os.getenv('WEATHER_API')
    if not api_key:
        raise RuntimeError('Missing WEATHER_API in environment')
    return f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={lat},{lon}"


def fetch_weather() -> dict:
    f"""
    Fetch current weather for inputted city and state from WeatherAPI.
    Returns a small dict with the specific fields needed by the frontend.
    """
    url = build_weather_url()
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    return {
        'city': data['location']['name'],
        'region': data['location']['region'],
        'country': data['location']['country'],
        'temperature_f': data['current']['temp_f'],
        'feels_like_f': data['current']['feelslike_f'],
        'condition_text': data['current']['condition']['text'],
        'last_updated': data['current']['last_updated']
    }


if __name__ == "__main__":
    load_dotenv()
    # Demo print when running this file directly
    try:
        result = fetch_weather()
        print(result)
    except Exception as e:
        print(f"Error: {e}")