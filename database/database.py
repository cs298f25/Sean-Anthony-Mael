import hashlib
import os
import sqlite3
from typing import Optional

# Database file path - store in the same directory as this script
DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')

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
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        # Table for storing users (must be created first)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Table for storing skill tests 
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DROP TABLE IF EXISTS skill_tests;")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS skill_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(name != ''),
                description TEXT NOT NULL CHECK(description != '')
            );
            """
        )
        

        # Table for storing user quiz results
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_test_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                score INTEGER DEFAULT 0 CHECK(score >= 0 AND score <= 100),
                total_questions INTEGER DEFAULT 0,
                FOREIGN KEY (skill_test_id) REFERENCES skill_tests(id)
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        # Table for storing question information
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DROP TABLE IF EXISTS questions;")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_test_id INTEGER NOT NULL,
                question_type TEXT NOT NULL DEFAULT 'text_input' CHECK(question_type IN ('multiple_choice', 'text_input')),
                prompt TEXT NOT NULL CHECK(prompt != ''),
                answer TEXT NOT NULL CHECK(answer != ''),
                category TEXT NOT NULL CHECK(category != ''),
                choices TEXT,
                FOREIGN KEY (skill_test_id) REFERENCES skill_tests(id)
            );
            """
        )
        
        # Add choices column to existing questions table if it doesn't exist (migration)
        ensure_choices_column(cursor)

        # Table for storing the questions in a quiz result
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_result_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_result_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL CHECK(user_answer != ''),
                is_correct BOOLEAN NOT NULL,
                FOREIGN KEY (quiz_result_id) REFERENCES quiz_results(id)
                FOREIGN KEY (question_id) REFERENCES questions(id)
            );
            """
            )

        # Table for storing user stats over time to track progress and improvement over time
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_skill_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                skill_test_id INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL CHECK(correct_answers >= 0),
                incorrect_answers INTEGER NOT NULL CHECK(incorrect_answers >= 0),
                FOREIGN KEY (user_id) REFERENCES users(id)
                FOREIGN KEY (skill_test_id) REFERENCES skill_tests(id)
            );
            """
        )

        # Table for storing study guides
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("DROP TABLE IF EXISTS study_guides;")
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS study_guides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_test_id INTEGER NOT NULL,
                content TEXT NOT NULL CHECK(content != ''),
                FOREIGN KEY (skill_test_id) REFERENCES skill_tests(id)
            );
            """
        )
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_results_user_id ON quiz_results(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_results_skill_test_id ON quiz_results(skill_test_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_result_questions_quiz_result_id ON quiz_result_questions(quiz_result_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_result_questions_question_id ON quiz_result_questions(question_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_skill_stats_user_id ON user_skill_stats(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_skill_stats_skill_test_id ON user_skill_stats(skill_test_id);")
        ensure_password_column(cursor)
        ensure_choices_column(cursor)
        conn.commit()
        print(f"Database initialized at {DB_PATH}")
        
        # Load and execute insert_data.sql if it exists and table is empty
        try:
            # Check if skill_tests table is empty
            cursor.execute("SELECT COUNT(*) as count FROM skill_tests")
            count = cursor.fetchone()['count']
            
            sql_file_path = os.path.join(os.path.dirname(__file__), 'insert_data.sql')
            if count == 0 and os.path.exists(sql_file_path):
                sql_content = read_sql_file('insert_data.sql')
                # Execute the SQL content
                try:
                    cursor.executescript(sql_content)
                    conn.commit()
                    print("Data from insert_data.sql loaded successfully")
                except Exception as sql_error:
                    print(f"Error executing insert_data.sql: {sql_error}")
                    conn.rollback()
        except Exception as e:
            print(f"Warning: Could not load insert_data.sql: {e}")
    finally:
        conn.close()


def create_user(username: str, password: Optional[str] = None):
    """Create a new user with optional password. Returns the user id if successful."""
    normalized_username = validate_username(username)
    password_hash = hash_password(password) if password else ''
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (normalized_username, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    finally:
        conn.close()


def get_user(username: str):
    """Get user information by username. Returns dict if found, None otherwise."""
    normalized_username = validate_username(username)
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (normalized_username,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def login_user(username: str, password: str) -> Optional[dict]:
    """Validate credentials. Returns user data on success, None on failure."""
    normalized_username = validate_username(username)
    if not password:
        raise ValueError("Password cannot be empty")

    user = get_user(normalized_username)
    if user is None:
        return None

    stored_hash = user.get("password_hash") or ""
    if not stored_hash:
        # Migrate existing users created without a password hash
        new_hash = hash_password(password)
        update_user_password(user["id"], new_hash)
        user["password_hash"] = new_hash
        return user

    if verify_password(password, stored_hash):
        return user
    return None


def hash_password(password: str) -> str:
    """Hash a password using PBKDF2."""
    if not password:
        raise ValueError("Password cannot be empty")
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return f"{salt.hex()}:{derived.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    if not stored_hash:
        return False
    try:
        salt_hex, hash_hex = stored_hash.split(":", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(hash_hex)
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
    return constant_time_compare(expected, candidate)


def constant_time_compare(val1: bytes, val2: bytes) -> bool:
    """Compare two bytes objects in constant time."""
    if len(val1) != len(val2):
        return False
    result = 0
    for x, y in zip(val1, val2):
        result |= x ^ y
    return result == 0


def validate_username(username: str) -> str:
    """Validate a username. Returns the username if valid, raises an error if invalid."""
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")
    return username.strip()


def update_user_password(user_id: int, password_hash: str) -> None:
    """Persist a newly generated password hash for legacy users."""
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (password_hash, user_id),
        )
        conn.commit()


def ensure_password_column(cursor: sqlite3.Cursor):
    """Add password_hash column for older databases."""
    cursor.execute("PRAGMA table_info(users)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "password_hash" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT NOT NULL DEFAULT ''")

def ensure_choices_column(cursor: sqlite3.Cursor):
    """Add choices column to questions table for multiple choice questions."""
    cursor.execute("PRAGMA table_info(questions)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "choices" not in columns:
        cursor.execute("ALTER TABLE questions ADD COLUMN choices TEXT")
    # Also ensure question_type has a default for existing rows
    cursor.execute("UPDATE questions SET question_type = 'text_input' WHERE question_type IS NULL OR question_type = ''")
