from dotenv import load_dotenv
import os
import requests

def build_weather_url(city: str = 'Bethlehem', state: str = 'PA') -> str:
    api_key = os.getenv('WEATHER_API')
    if not api_key:
        raise RuntimeError('Missing WEATHER_API in environment')
    return f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city},%20{state}"


def fetch_weather() -> dict:
    f"""
    Fetch current weather for inputted city and state from WeatherAPI.
    Returns a small dict with the specific fields needed by the frontend.
    """
    url = build_weather_url('Bethlehem', 'PA')
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