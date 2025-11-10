import os
import dotenv
import requests

api_key = os.getenv('MUSIC_KEY')
if not api_key:
    raise ValueError("MUSIC_KEY environment variable is not set. Please create a .env file with your Music API key.")

"""
Get the top genres from the Music API.
"""
def get_top_genres() -> list[str]:
    url = f"https://ws.audioscrobbler.com/2.0/?method=tag.getTopTags&api_key={api_key}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()['toptags']['tag']
    return [genre['name'] for genre in data]

"""
Get the top artists from the Music API.
"""
def get_top_artists() -> list[str]:
    url = f"https://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag=disco&api_key={api_key}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()['artists']['artist']
    return [artist['name'] for artist in data]