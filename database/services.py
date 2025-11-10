from operator import ge
import sqlite3
import uuid
from typing import Optional, Dict, List
from database import get_db_connection, read_sql_file
import music

def create_user(name: Optional[str] = None, latitude: Optional[float] = None, 
                longitude: Optional[float] = None) -> str:
    user_id = str(uuid.uuid4())
    try:
        with get_db_connection() as conn: 
            conn.execute('''
                INSERT INTO users (user_id, name, latitude, longitude)
                VALUES (?, ?, ?, ?)
            ''', (user_id, name, latitude, longitude))
            conn.commit()
        return user_id
    except sqlite3.Error as e:
        print(f"Error creating user: {e}")
        raise 

def get_user(user_id: str) -> Optional[Dict]:
    """Get user by user_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def update_user_location(user_id: str, latitude: float, longitude: float):
    """Update user's location."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET latitude = ?, longitude = ?, last_updated = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (latitude, longitude, user_id))
    
    conn.commit()
    conn.close()

def update_user_name(user_id: str, name: str):
    """Update user's name."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET name = ?, last_updated = CURRENT_TIMESTAMP
        WHERE user_id = ?
    ''', (name, user_id))
    
    conn.commit()
    conn.close()


# ---------------------------
# Ingestion from Last.fm API
# ---------------------------

def fetch_and_store_tracks_by_artist(artist_id: int, artist_name: str) -> list[dict]:
    """
    Fetches top tracks for an artist, inserts new ones,
    and returns them from the local DB.
    """
    print(f"Fetching tracks from artist: {artist_name}")
    try:
        tracks_data = music.get_artist_top_tracks(artist_name)
    except Exception as e:
        print(f"API call failed: {e}")
        return []
    if not tracks_data:
        return []
    sql_query = read_sql_file('database/insert_data.sql')
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

        for track in tracks_data:
            params = (
                artist_name,
                track['name'],
                track.get('duration', 0),
                track['name'],
                artist_name
            )
            cursor.executescript(sql_query, params)

        conn.commit()

        query = """
            SELECT t.track_id, t.title, t.duration
            FROM tracks t
            JOIN track_artists ta ON t.track_id = ta.track_id
            WHERE ta.artist_id = ? 
            """
        rows = conn.execute(query, (artist_id, )).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

def fetch_and_store_artists_by_genre(genre: str) -> list[dict]:
    """
    Fetches artists for a genre from the API, inserts new ones into the DB,
    and returns the list of artists from the DB.
    """
    print(f"Fetching artists by genre: {genre}")
    try:
        artist_names = music.get_top_artists_by_genre(genre, limit=50)
    except Exception as e:
        print(f"API call failed: {e}")
        return []
    if not artist_names:
        return []

    artists_to_insert = [(name,) for name in artist_names]
    sql_insert_query = "INSERT OR IGNORE artists (name) VALUES (?);"
    
    try:
        with get_db_connection() as conn:
            # 3. Insert all new artists in a single transaction
            conn.executemany(sql_insert_query, artists_to_insert)
            conn.commit()
            
            # 4. Query your LOCAL DB to get the full records
            placeholders = ','.join(['?'] * len(artist_names))
            sql_select_query = f"SELECT artist_id, name FROM artists WHERE name IN ({placeholders})"
            
            rows = conn.execute(sql_select_query, artist_names).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []

# ---------------------------
# Discovery/query helpers
# ---------------------------

def get_artist_by_name(artist_name: str) -> Optional[Dict]:
    """
    Finds a single artist in the DB by their exact name
    """
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT artist_id, name FROM artists WHERE name = ?",
            (artist_name,)
        ).fetchone()
        return dict(row) if row else None

def get_and_store_tracks_for_artist(artist_name: str) -> List[Dict]:
    """
    AI-friendly wrapper. Finds an artist, then fetches and stores their tracks 
    """
    artist = get_artist_by_name(artist_name)
    if not artist:
        return []
    return fetch_and_store_tracks_by_artist(
        artist_id=artist['artist_id'],
        artist_name=artist['name']
    )