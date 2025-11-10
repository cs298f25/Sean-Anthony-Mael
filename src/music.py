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
Get the top artists by genre from the Music API.
"""
def get_top_artists_by_genre(genre: str) -> list[str]:
    url = f"https://ws.audioscrobbler.com/2.0/?method=tag.gettopartists&tag={genre}&api_key={api_key}&format=json"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()['artists']['artist']
    return [artist['name'] for artist in data]


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
