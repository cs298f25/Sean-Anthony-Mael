import sqlite3
import os

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')

def get_db_connection():
    """Get a database connection."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def read_sql_file(file_path: str) -> str:
    """Reads a SQL file and returns its content as a string."""
    # Construct a path relative to this script
    base_dir = os.path.dirname(__file__)
    full_path = os.path.join(base_dir, file_path)
    with open(full_path, 'r') as f:
        return f.read()

def init_database():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
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
        CREATE TABLE IF NOT EXISTS artists (
            artist_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create albums table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS albums (
            album_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist_id INTEGER NOT NULL,
            FOREIGN KEY (artist_id) REFERENCES artists (artist_id)
        )
    ''')

    # Create genres table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS genres (
            genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create tracks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracks (
            track_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist_id INTEGER NOT NULL,
            album_id INTEGER NOT NULL,
            duration INTEGER, -- in seconds,
            metadata TEXT,
            FOREIGN KEY (artist_id) REFERENCES artists (artist_id),
            FOREIGN KEY (album_id) REFERENCES albums (album_id)
        )
    ''')

    # Link tracks to one or more artists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS track_artists (
            track_id INTEGER NOT NULL,
            artist_id INTEGER NOT NULL,
            role TEXT DEFAULT 'main', -- main, featured, producer, etc.
            PRIMARY KEY (track_id, artist_id, role),
            FOREIGN KEY (track_id) REFERENCES tracks (track_id) ON DELETE CASCADE,
            FOREIGN KEY (artist_id) REFERENCES artists (artist_id) ON DELETE CASCADE
        )
    ''')

    # Link tracks to one or more genres
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS track_genres (
            track_id INTEGER NOT NULL,
            genre_id INTEGER NOT NULL,
            PRIMARY KEY (track_id, genre_id),
            FOREIGN KEY (track_id) REFERENCES tracks (track_id),
            FOREIGN KEY (genre_id) REFERENCES genres (genre_id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")



