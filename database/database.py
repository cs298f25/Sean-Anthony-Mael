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
                skill_test_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
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
                skill_test_id INTEGER NOT NULL,
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
        
        # Create indexes for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_results_user_id ON quiz_results(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_results_skill_test_id ON quiz_results(skill_test_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_result_questions_quiz_result_id ON quiz_result_questions(quiz_result_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quiz_result_questions_question_id ON quiz_result_questions(question_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_skill_stats_user_id ON user_skill_stats(user_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_skill_stats_skill_test_id ON user_skill_stats(skill_test_id);")
        conn.commit()
        print(f"Database initialized at {DB_PATH}")
        
        # Load and execute insert_data.sql if it exists and table is empty
        try:
            # Check if skill_tests table is empty
            cursor.execute("SELECT COUNT(*) as count FROM skill_tests")
            count = cursor.fetchone()['count']
            
            if count == 0:
                sql_file_path = os.path.join(os.path.dirname(__file__), 'insert_data.sql')
                if os.path.exists(sql_file_path):
                    sql_content = read_sql_file('insert_data.sql')
                    # Execute the SQL content
                    cursor.executescript(sql_content)
                    conn.commit()
                    print("Data from insert_data.sql loaded successfully")
            else:
                print(f"Skill tests table already has {count} entries, skipping insert_data.sql")
        except Exception as e:
            print(f"Warning: Could not load insert_data.sql: {e}")
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

