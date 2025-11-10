import sqlite3
import os
from typing import Optional, Dict, List
import uuid

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'app.db')

def get_db_connection():
    """Get a database connection."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Music table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS music (
            music_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT,
            album TEXT,
            genre TEXT,
            year INTEGER,
            duration INTEGER,
            file_path TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

def create_user(name: Optional[str] = None, latitude: Optional[float] = None, 
                longitude: Optional[float] = None) -> str:
    """Create a new user and return their user_id."""
    user_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (user_id, name, latitude, longitude)
        VALUES (?, ?, ?, ?)
    ''', (user_id, name, latitude, longitude))
    
    conn.commit()
    conn.close()
    return user_id

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

def add_music(title: str, artist: Optional[str] = None, album: Optional[str] = None,
              genre: Optional[str] = None, year: Optional[int] = None,
              duration: Optional[int] = None, file_path: Optional[str] = None,
              metadata: Optional[str] = None) -> int:
    """Add a new music entry and return music_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO music (title, artist, album, genre, year, duration, file_path, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, artist, album, genre, year, duration, file_path, metadata))
    
    music_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return music_id

def get_music(music_id: int) -> Optional[Dict]:
    """Get music by music_id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM music WHERE music_id = ?', (music_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_all_music() -> List[Dict]:
    """Get all music entries."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM music ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def update_music(music_id: int, **kwargs) -> bool:
    """Update music entry. Returns True if updated, False if not found."""
    allowed_fields = ['title', 'artist', 'album', 'genre', 'year', 'duration', 'file_path', 'metadata']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return False
    
    # Always update the updated_at timestamp
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()] + ['updated_at = CURRENT_TIMESTAMP'])
    values = list(updates.values()) + [music_id]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(f'UPDATE music SET {set_clause} WHERE music_id = ?', values)
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return updated

def delete_music(music_id: int) -> bool:
    """Delete music entry. Returns True if deleted, False if not found."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM music WHERE music_id = ?', (music_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    return deleted

