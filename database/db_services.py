from database.database import get_db_connection

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
        if rows:
            return [dict(row) for row in rows]
        else:
            return []
    except Exception as e:
        print(f"Error listing skill tests: {e}")
        return []
    finally:
        conn.close()

def get_skill_test_questions(skill_test_id: int, limit: int = 10):
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

def get_correct_answers(session_id: int):
    """Get the correct answers for a quiz session. Returns a list of correct answers if successful, None otherwise."""
    if not session_id:
        raise ValueError("Session ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_result_questions WHERE session_id = ? AND is_correct = 1", (session_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_incorrect_answers(session_id: int):
    """Get the incorrect answers for a quiz session. Returns a list of incorrect answers if successful, None otherwise."""
    if not session_id:
        raise ValueError("Session ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_result_questions WHERE session_id = ? AND is_correct = 0", (session_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()