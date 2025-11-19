import sqlite3
import os

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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Table for storing user quiz results
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_quiz_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                questions_correct INTEGER NOT NULL CHECK(questions_correct >= 0),
                total_questions INTEGER NOT NULL CHECK(total_questions > 0),
                category TEXT NOT NULL CHECK(category != ''),
                CHECK(questions_correct <= total_questions),
                quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username)
            );
            """
        )
        
        # Table for storing question statistics by category
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS question_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL CHECK(question_text != ''),
                category TEXT NOT NULL CHECK(category != ''),
                right_count INTEGER DEFAULT 0,
                wrong_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(question_text, category)
            );
            """
        )
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_quiz_username ON user_quiz_results(username);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_quiz_category ON user_quiz_results(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_question_stats_category ON question_stats(category);")
        conn.commit()
        print(f"Database initialized at {DB_PATH}")
    finally:
        conn.close()


def create_user(username: str):
    """Create a new user. Returns the user id if successful, None if user already exists."""
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username)
            VALUES (?)
            """,
            (username.strip(),)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        # User already exists
        return None
    finally:
        conn.close()


def get_user(username: str):
    """Get user information by username. Returns dict if found, None otherwise."""
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username.strip(),)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def add_user_quiz_result(username: str, questions_correct: int, total_questions: int, category: str):
    """Add a user quiz result to the database. Creates the user if they don't exist."""
    # Validate inputs
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")
    if questions_correct < 0:
        raise ValueError("questions_correct cannot be negative")
    if total_questions <= 0:
        raise ValueError("total_questions must be positive")
    if questions_correct > total_questions:
        raise ValueError("questions_correct cannot exceed total_questions")
    if not category or not category.strip():
        raise ValueError("Category cannot be empty")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Ensure user exists first (due to foreign key constraint)
        create_user(username.strip())
        
        cursor.execute(
            """
            INSERT INTO user_quiz_results (username, questions_correct, total_questions, category)
            VALUES (?, ?, ?, ?)
            """,
            (username.strip(), questions_correct, total_questions, category.strip())
        )
        conn.commit()
        result_id = cursor.lastrowid
        return result_id
    finally:
        conn.close()


def get_user_quiz_results(username: str = None, category: str = None):
    """Get user quiz results. Can filter by username and/or category."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        query = "SELECT * FROM user_quiz_results WHERE 1=1"
        params = []
        
        if username:
            query += " AND username = ?"
            params.append(username.strip())
        
        if category:
            query += " AND category = ?"
            params.append(category.strip())
        
        query += " ORDER BY quiz_date DESC"
        
        cursor.execute(query, params)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    finally:
        conn.close()


def update_question_stats(question_text: str, category: str, is_correct: bool):
    """Update question statistics. Increments right_count or wrong_count."""
    if not question_text or not question_text.strip():
        raise ValueError("question_text cannot be empty")
    if not category or not category.strip():
        raise ValueError("Category cannot be empty")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Use INSERT ... ON CONFLICT for atomic upsert operation
        if is_correct:
            cursor.execute(
                """
                INSERT INTO question_stats (question_text, category, right_count, wrong_count, created_at, updated_at)
                VALUES (?, ?, 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(question_text, category) 
                DO UPDATE SET 
                    right_count = right_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (question_text.strip(), category.strip())
            )
        else:
            cursor.execute(
                """
                INSERT INTO question_stats (question_text, category, right_count, wrong_count, created_at, updated_at)
                VALUES (?, ?, 0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ON CONFLICT(question_text, category) 
                DO UPDATE SET 
                    wrong_count = wrong_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (question_text.strip(), category.strip())
            )
        
        conn.commit()
    finally:
        conn.close()


def get_question_stats(category: str = None):
    """Get question statistics. Can filter by category."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                "SELECT * FROM question_stats WHERE category = ? ORDER BY updated_at DESC",
                (category.strip(),)
            )
        else:
            cursor.execute("SELECT * FROM question_stats ORDER BY updated_at DESC")
        
        results = [dict(row) for row in cursor.fetchall()]
        return results
    finally:
        conn.close()


def get_category_stats():
    """Get aggregated statistics by category."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT 
                category,
                SUM(right_count) as total_right,
                SUM(wrong_count) as total_wrong,
                COUNT(*) as question_count
            FROM question_stats
            GROUP BY category
            ORDER BY category
            """
        )
        
        results = [dict(row) for row in cursor.fetchall()]
        return results
    finally:
        conn.close()

