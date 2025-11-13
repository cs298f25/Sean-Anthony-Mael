import sqlite3
import uuid
import traceback
from typing import Any, Optional, Dict, List
from .database import get_db_connection, read_sql_file
import sys
from pathlib import Path

# Add src directory to path for music import (must be before importing music)
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
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
        return dict[Any, Any](row)
    return None

def update_user_location(user_id: str, latitude: float, longitude: float):
    """Update user's location."""
    try:
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE users 
                SET latitude = ?, longitude = ?, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (latitude, longitude, user_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating user location: {e}")
        raise

def update_user_name(user_id: str, name: str):
    """Update user's name."""
    try:
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE users 
                SET name = ?, last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (name, user_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating user name: {e}")
        raise

def update_user_visit(user_id: str):
    """Update user's last_updated timestamp when they visit the site."""
    try:
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE users 
                SET last_updated = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error updating user visit: {e}")
        raise

def populate_genres_if_empty():
    """Populate genres table from insert_data.sql if it's empty."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Check if genres table is empty
            count = cursor.execute('SELECT COUNT(*) FROM genres').fetchone()[0]
            if count == 0:
                print("Genres table is empty, populating from insert_data.sql...")
                sql_content = read_sql_file('insert_data.sql')
                if sql_content:
                    cursor.executescript(sql_content)
                    conn.commit()
                    print("Genres table populated successfully")
                    return True
            return False
    except Exception as e:
        print(f"Error populating genres: {e}")
        traceback.print_exc()
        return False

def link_track_to_genre(track_id: int, genre_name: str) -> bool:
    """
    Link a track to a genre. Creates the genre if it doesn't exist.
    Returns True if successful, False otherwise.
    """
    try:
        with get_db_connection() as conn:
            # Get or create genre
            genre_row = conn.execute(
                'SELECT genre_id FROM genres WHERE name = ?',
                (genre_name.lower(),)
            ).fetchone()
            
            if genre_row:
                genre_id = genre_row['genre_id']
            else:
                # Create genre if it doesn't exist
                cursor = conn.execute(
                    'INSERT INTO genres (name) VALUES (?)',
                    (genre_name.lower(),)
                )
                genre_id = cursor.lastrowid
            
            # Link track to genre
            conn.execute('''
                INSERT OR IGNORE INTO track_genres (track_id, genre_id)
                VALUES (?, ?)
            ''', (track_id, genre_id))
            conn.commit()
            return True
    except sqlite3.Error as e:
        print(f"Error linking track {track_id} to genre {genre_name}: {e}")
        return False

def add_music(title: str, artist: Optional[str] = None, album: Optional[str] = None,
              genre: Optional[str] = None, year: Optional[int] = None,
              duration: Optional[int] = None, file_path: Optional[str] = None,
              metadata: Optional[str] = None) -> int:
    """Add a new music entry and return track_id."""
    try:
        with get_db_connection() as conn:
            # Get or create artist
            artist_id = None
            if artist:
                row = conn.execute('SELECT artist_id FROM artists WHERE name = ?', (artist,)).fetchone()
                if row:
                    artist_id = row['artist_id']
                else:
                    cursor = conn.execute('INSERT INTO artists (name) VALUES (?)', (artist,))
                    artist_id = cursor.lastrowid
            
            # Get or create album (need a default album if none provided)
            album_id = None
            if album and artist_id:
                row = conn.execute('SELECT album_id FROM albums WHERE title = ? AND artist_id = ?', 
                    (album, artist_id)).fetchone()
                if row:
                    album_id = row['album_id']
                else:
                    cursor = conn.execute('INSERT INTO albums (title, artist_id) VALUES (?, ?)', 
                                        (album, artist_id))
                    album_id = cursor.lastrowid
            elif artist_id:
                # Create a default album if no album specified
                cursor = conn.execute('INSERT INTO albums (title, artist_id) VALUES (?, ?)', 
                                    ('Unknown Album', artist_id))
                album_id = cursor.lastrowid
            
            if not artist_id or not album_id:
                raise ValueError("Artist and album are required")
            
            # Insert track
            cursor = conn.execute('''
                INSERT INTO tracks (title, artist_id, album_id, duration, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, artist_id, album_id, duration, metadata))
            track_id = cursor.lastrowid
            conn.commit()
            return track_id
    except sqlite3.Error as e:
        print(f"Error adding music: {e}")
        raise

def get_music(track_id: int) -> Optional[Dict]:
    """Get music/track by track_id."""
    try:
        with get_db_connection() as conn:
            row = conn.execute('SELECT * FROM tracks WHERE track_id = ?', (track_id,)).fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Error getting music: {e}")
        return None


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
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get or create a default album for this artist
            album_row = conn.execute(
                'SELECT album_id FROM albums WHERE title = ? AND artist_id = ?',
                ('Unknown Album', artist_id)
            ).fetchone()
            
            if album_row:
                album_id = album_row['album_id']
            else:
                cursor.execute(
                    'INSERT INTO albums (title, artist_id) VALUES (?, ?)',
                    ('Unknown Album', artist_id)
                )
                album_id = cursor.lastrowid

            for track in tracks_data:
                # Check if track already exists
                existing_track = conn.execute('''
                    SELECT track_id FROM tracks 
                    WHERE title = ? AND artist_id = ? AND album_id = ?
                ''', (track['name'], artist_id, album_id)).fetchone()
                
                if existing_track:
                    track_id = existing_track['track_id']
                else:
                    # Insert track
                    cursor.execute('''
                        INSERT INTO tracks (title, artist_id, album_id, duration)
                        VALUES (?, ?, ?, ?)
                    ''', (track['name'], artist_id, album_id, track.get('duration', 0)))
                    track_id = cursor.lastrowid
                
                # Link track to artist (if not already linked)
                if track_id:
                    cursor.execute('''
                        INSERT OR IGNORE INTO track_artists (track_id, artist_id, role)
                        VALUES (?, ?, 'main')
                    ''', (track_id, artist_id))

            conn.commit()

            # Query tracks for this artist (include artist name for better presentation)
            query = """
                SELECT t.track_id, t.title, t.duration, a.name as artist_name
                FROM tracks t
                JOIN track_artists ta ON t.track_id = ta.track_id
                JOIN artists a ON ta.artist_id = a.artist_id
                WHERE ta.artist_id = ? 
            """
            rows = conn.execute(query, (artist_id,)).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        traceback.print_exc()
        return []

def fetch_and_store_artists_by_genre(genre: str) -> list[dict]:
    """
    Fetches artists for a genre from the API, inserts new ones into the DB,
    and returns the list of artists from the DB.
    """
    print(f"Fetching artists by genre: {genre}")
    try:
        artist_names = music.get_top_artists_by_genre(genre)
        print(f"[DEBUG] API returned {len(artist_names) if artist_names else 0} artists")
    except Exception as e:
        print(f"API call failed: {e}")
        traceback.print_exc()
        # Return error info instead of empty list
        return [{"error": f"API call failed: {str(e)}", "genre": genre}]
    
    if not artist_names:
        print(f"[DEBUG] No artists returned from API for genre: {genre}")
        # Return error info so bot knows what happened
        return [{"error": f"No artists found for genre '{genre}'. The genre might not exist or the API returned no results.", "genre": genre}]

    artists_to_insert = [(name,) for name in artist_names]
    sql_query = "INSERT OR IGNORE INTO artists (name) VALUES (?);"
    
    try:
        with get_db_connection() as conn:
            # Insert all new artists in a single transaction
            cursor = conn.cursor()
            cursor.executemany(sql_query, artists_to_insert)
            inserted_count = cursor.rowcount
            conn.commit()
            print(f"[DEBUG] Inserted {inserted_count} artists into database")
            
            # Query your LOCAL DB to get the full records
            placeholders = ','.join(['?'] * len(artist_names))
            sql_select_query = f"SELECT artist_id, name FROM artists WHERE name IN ({placeholders})"
            
            rows = conn.execute(sql_select_query, artist_names).fetchall()
            result = [dict(row) for row in rows]
            # Limit to 15 artists for faster responses
            limited_result = result[:15]
            print(f"[DEBUG] Retrieved {len(result)} artists from database, returning {len(limited_result)}")
            return limited_result
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        traceback.print_exc()
        return []

def fetch_and_store_chart_tracks() -> List[Dict]:
    """
    Fetches top chart tracks, inserts them, and returns them.
    This is a great tool for "what's popular" recommendations.
    """
    print("Fetching top chart tracks...")
    try:
        tracks_data = music.get_chart_top_tracks()
    except Exception as e:
        print(f"API call failed: {e}")
        return []
    
    if not tracks_data:
        return []

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            stored_tracks = []
            
            for track in tracks_data:
                artist_name = track.get('artist', 'Unknown Artist')
                track_name = track.get('name', 'Unknown Track')
                duration = track.get('duration', 0)
                
                # Get or create artist
                artist_row = conn.execute(
                    'SELECT artist_id FROM artists WHERE name = ?',
                    (artist_name,)
                ).fetchone()
                
                if artist_row:
                    artist_id = artist_row['artist_id']
                else:
                    cursor.execute('INSERT INTO artists (name) VALUES (?)', (artist_name,))
                    artist_id = cursor.lastrowid
                
                # Get or create a default album for this artist
                album_row = conn.execute(
                    'SELECT album_id FROM albums WHERE title = ? AND artist_id = ?',
                    ('Unknown Album', artist_id)
                ).fetchone()
                
                if album_row:
                    album_id = album_row['album_id']
                else:
                    cursor.execute(
                        'INSERT INTO albums (title, artist_id) VALUES (?, ?)',
                        ('Unknown Album', artist_id)
                    )
                    album_id = cursor.lastrowid
                
                # Check if track already exists
                existing_track = conn.execute('''
                    SELECT track_id FROM tracks 
                    WHERE title = ? AND artist_id = ? AND album_id = ?
                ''', (track_name, artist_id, album_id)).fetchone()
                
                if existing_track:
                    track_id = existing_track['track_id']
                else:
                    # Insert track
                    cursor.execute('''
                        INSERT INTO tracks (title, artist_id, album_id, duration)
                        VALUES (?, ?, ?, ?)
                    ''', (track_name, artist_id, album_id, duration))
                    track_id = cursor.lastrowid
                
                # Link track to artist
                if track_id:
                    cursor.execute('''
                        INSERT OR IGNORE INTO track_artists (track_id, artist_id, role)
                        VALUES (?, ?, 'main')
                    ''', (track_id, artist_id))
                    
                    # Store track info with artist name for easy display
                    stored_tracks.append({
                        'title': track_name,
                        'artist': artist_name,
                        'duration': duration,
                        'track_id': track_id
                    })
            
            conn.commit()
            # Limit to 20 tracks for better responses
            return stored_tracks[:20]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        traceback.print_exc()
        return []

def fetch_and_store_similar_artists(artist_name: str) -> List[Dict]:
    """
    Fetches artists similar to a given artist, stores them,
    and returns them from the DB.
    """
    print(f"Fetching artists similar to {artist_name}...")
    try:
        artist_names = music.get_similar_artists(artist_name)
    except Exception as e:
        print(f"API call failed: {e}")
        return []
    
    if not artist_names:
        return []

    artists_to_insert = [(name,) for name in artist_names]
    sql_insert_query = "INSERT OR IGNORE INTO artists (name) VALUES (?);"
    
    try:
        with get_db_connection() as conn:
            conn.executemany(sql_insert_query, artists_to_insert)
            conn.commit()
            
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

def get_and_store_tracks_for_artist_by_name(artist_name: str) -> List[Dict]:
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

def fetch_and_store_tracks_by_genre(genre: str, max_artists: int = 5) -> List[Dict]:
    """
    Fetches artists for a genre, then fetches and stores their top tracks.
    Returns a list of tracks from artists in that genre.
    This is the best tool for getting song recommendations by genre.
    """
    print(f"Fetching tracks by genre: {genre}")
    
    # Ensure genres table is populated
    populate_genres_if_empty()
    
    # First, get artists for this genre
    artists = fetch_and_store_artists_by_genre(genre)
    
    if not artists or len(artists) == 0:
        print(f"[ERROR] No artists found for genre: {genre}")
        return []
    
    # Check if first item is an error
    if isinstance(artists[0], dict) and 'error' in artists[0]:
        print(f"[ERROR] Failed to fetch artists for genre: {genre}")
        return []
    
    # Limit the number of artists to fetch tracks for (to avoid too many API calls)
    artists_to_process = artists[:max_artists]
    print(f"[DEBUG] Fetching tracks for {len(artists_to_process)} artists in genre: {genre}")
    
    all_tracks = []
    
    try:
        for artist in artists_to_process:
            artist_id = artist.get('artist_id')
            artist_name = artist.get('name')
            
            if not artist_id or not artist_name:
                continue
            
            try:
                # Fetch and store tracks for this artist
                tracks = fetch_and_store_tracks_by_artist(artist_id, artist_name)
                # Ensure tracks have 'artist' field for consistency
                # Also link tracks to the genre
                for track in tracks:
                    if 'artist_name' in track and 'artist' not in track:
                        track['artist'] = track['artist_name']
                    # Link track to genre
                    track_id = track.get('track_id')
                    if track_id:
                        try:
                            link_track_to_genre(track_id, genre)
                        except Exception as e:
                            print(f"[WARNING] Failed to link track {track_id} to genre {genre}: {e}")
                            # Continue even if linking fails
                all_tracks.extend(tracks)
                print(f"[DEBUG] Found {len(tracks)} tracks for artist: {artist_name}, linked to genre: {genre}")
            except Exception as e:
                print(f"[ERROR] Failed to fetch tracks for artist {artist_name}: {e}")
                traceback.print_exc()
                continue
        
        # Limit total tracks returned to avoid overwhelming the AI
        limited_tracks = all_tracks[:20]
        print(f"[DEBUG] Returning {len(limited_tracks)} tracks for genre: {genre}")
        return limited_tracks
        
    except Exception as e:
        print(f"[ERROR] Error fetching tracks by genre: {e}")
        traceback.print_exc()
        return []
