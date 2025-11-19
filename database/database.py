import sqlite3
import os
from database import insert_data

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

        # Table for storing skill tests 
        cursor.execute(
            f"""
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
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP NOT NULL,
                score INTEGER NOT NULL CHECK(score >= 0 AND score <= 100),
                total_questions INTEGER NOT NULL CHECK(total_questions > 0),
                FOREIGN KEY (skill_test_id) REFERENCES skill_tests(id)
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        # Table for storing question information
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL CHECK(prompt != ''),
                answer TEXT NOT NULL CHECK(answer != ''),
                category TEXT NOT NULL CHECK(category != ''),
                FOREIGN KEY (skill_test_id) REFERENCES skill_tests(id)
            );
            """
        )

        # Table for storing the questions in a quiz result
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_result_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_results_user_id ON quiz_results(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_results_skill_test_id ON quiz_results(skill_test_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_result_questions_quiz_result_id ON quiz_result_questions(quiz_result_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_result_questions_question_id ON quiz_result_questions(question_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_skill_stats_user_id ON user_skill_stats(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_skill_stats_skill_test_id ON user_skill_stats(skill_test_id);")
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

def start_quiz_session(user_id: int, skill_test_id: int) -> int:
    """Start a new quiz session for a user and skill test. Returns the quiz result id if successful, None otherwise."""
    if not user_id or not skill_test_id:
        raise ValueError("User ID and skill test ID are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_results (user_id, skill_test_id, start_time)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            """,
            (user_id, skill_test_id)
        )
        conn.commit()
        quiz_result_id = cursor.lastrowid
        return quiz_result_id
    finally:
        conn.close()

def finish_quiz_session(quiz_result_id: int, score: int, total_questions: int):
    """Finish a quiz session for a user and skill test. Returns True if successful, False otherwise."""
    if not quiz_result_id or not score or not total_questions:
        raise ValueError("Quiz result ID, score, and total questions are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE quiz_results SET end_time = CURRENT_TIMESTAMP, score = ?, total_questions = ? WHERE id = ?
            """,
            (score, total_questions, quiz_result_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def list_skill_tests():
    """List all skill tests. Returns a list of skill test dictionaries if successful, None otherwise."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skill_tests")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_skill_test_questions(skill_test_id: int, limit: int = 20):
    """Get the questions for a skill test. Returns a list of question dictionaries if successful, None otherwise."""
    if not skill_test_id or not limit:
        raise ValueError("Skill test ID and limit are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE skill_test_id = ? LIMIT ?", (skill_test_id, limit))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def record_user_answer(session_id: int, question_id: int, user_answer: str, is_correct: bool):
    """Record a user answer for a question in a quiz result. Returns True if successful, False otherwise."""
    if not session_id or not question_id or not user_answer or not is_correct:
        raise ValueError("Session ID, question ID, user answer, and is correct are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_result_questions (session_id, question_id, user_answer, is_correct)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, question_id, user_answer, is_correct)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def update_question_stats(question_id: int, correct_answers: int, incorrect_answers: int):
    """Update the question stats for a question. Returns True if successful, False otherwise."""
    if not question_id or not correct_answers or not incorrect_answers:
        raise ValueError("Question ID, correct answers, and incorrect answers are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE questions SET correct_answers = ?, incorrect_answers = ? WHERE id = ?
            """,
            (correct_answers, incorrect_answers, question_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def update_user_skill_stats(user_id: int, skill_test_id: int, correct_answers: int, incorrect_answers: int):
    """Update the user skill stats for a skill test. Returns True if successful, False otherwise."""
    if not user_id or not skill_test_id or not correct_answers or not incorrect_answers:
        raise ValueError("User ID, skill test ID, correct answers, and incorrect answers are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE user_skill_stats SET correct_answers = ?, incorrect_answers = ? WHERE user_id = ? AND skill_test_id = ?
            )
            """,
            (correct_answers, incorrect_answers, user_id, skill_test_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def get_quiz_session(session_id: int):
    """Get a quiz session by session ID. Returns a quiz session dictionary if successful, None otherwise."""
    if not session_id:
        raise ValueError("Session ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_results WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def get_user_history(user_id: int):
    """Get the history of quiz sessions for a user. Returns a list of quiz session dictionaries if successful, None otherwise."""
    if not user_id:
        raise ValueError("User ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_results WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_skill_test_leaderboard(skill_test_id: int):
    """Get the leaderboard for a skill test. Returns a list of user dictionaries if successful, None otherwise."""
    if not skill_test_id:
        raise ValueError("Skill test ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_results WHERE skill_test_id = ? ORDER BY score DESC", (skill_test_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_user_performance(user_id: int):
    """Get the performance of a user across all skill tests. Returns a list of skill test dictionaries if successful, None otherwise."""
    if not user_id:
        raise ValueError("User ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_skill_stats WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

