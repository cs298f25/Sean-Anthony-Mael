import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

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
Get the top artists by genre from the Music API.
"""
def get_top_artists_by_genre(genre: str) -> list[str]:
    url = f"https://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag={genre}&api_key={api_key}&format=json&limit=25"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        json_data = response.json()
        
        # Check for API errors
        if 'error' in json_data:
            error_msg = json_data.get('message', 'Unknown error')
            print(f"[ERROR] Last.fm API error for genre '{genre}': {error_msg}")
            return []
        
        # Validate response structure
        if 'artists' not in json_data:
            print(f"[ERROR] Missing 'artists' key in API response for genre: {genre}")
            return []
        
        if 'artist' not in json_data['artists']:
            print(f"[ERROR] No 'artist' key in API response for genre: {genre}")
            return []
        
        artist_data = json_data['artists']['artist']
        
        # Handle case where API returns a single artist object instead of a list
        if isinstance(artist_data, dict):
            artist_data = [artist_data]
        elif not isinstance(artist_data, list):
            print(f"[ERROR] Unexpected artist data format for genre: {genre}")
            return []
        
        artists = [artist['name'] for artist in artist_data if 'name' in artist]
        print(f"[DEBUG] Found {len(artists)} artists for genre: {genre}")
        return artists
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed for genre '{genre}': {e}")
        return []
    except (KeyError, ValueError, TypeError) as e:
        print(f"[ERROR] Failed to parse API response for genre '{genre}': {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error getting artists for genre '{genre}': {e}")
        return []

"""
Get the artist info from the Music API.
"""
def get_artist_info(artist_name: str) -> dict:
    url = f"https://ws.audioscrobbler.com/2.0/?method=artist.getInfo&artist={artist_name}&api_key={api_key}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()['artist']
    return {
        'name': data['name'],
        'bio': data['bio']['summary'],
        'genres': data['genres']['genre']
    }

"""
Get the artist top tracks from the Music API.
"""
def get_artist_top_tracks(artist_name: str) -> list[dict]:
    url = f"https://ws.audioscrobbler.com/2.0/?method=artist.getTopTracks&artist={artist_name}&api_key={api_key}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()['tracks']['track']
    return [
        {
            'name': track['name'],
            'artist': artist_name,
            'duration': int(track.get('duration', 0))
    }
    for track in data
    ]

"""
Get the chart top tracks from the Music API.
"""
def get_chart_top_tracks() -> dict[str]:
    url = f"https://ws.audioscrobbler.com/2.0/?method=chart.getTopTracks&api_key={api_key}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()['tracks']['track']
    return [
        {
            'name': track['name'],
            'artist': track['artist']['name'],
            'duration': int(track.get('duration', 0))
        }
        for track in data
    ]

"""
Get the similar artists from the Music API.
"""
def get_similar_artists(artist_name: str) -> list[str]:
    url = f"https://ws.audioscrobbler.com/2.0/?method=artist.getSimilar&artist={artist_name}&api_key={api_key}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()['similarartists']['artist']
    return [artist['name'] for artist in data]