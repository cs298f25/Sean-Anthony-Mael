from database.database import get_db_connection

def start_quiz_session(user_id: int, skill_test_id: int, total_questions: int = 10) -> int:
    """Start a new quiz session for a user and skill test. Returns the quiz result id."""
    if not user_id or not skill_test_id:
        raise ValueError("User ID and skill test ID are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_results (user_id, skill_test_id, start_time, end_time, score, total_questions)
            VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0, ?)
            """,
            (user_id, skill_test_id, max(1, total_questions))
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def finish_quiz_session(quiz_result_id: int, score: int, total_questions: int):
    """Finish a quiz session for a user and skill test."""
    if not quiz_result_id:
        raise ValueError("Quiz result ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE quiz_results SET end_time = CURRENT_TIMESTAMP, score = ?, total_questions = ? WHERE id = ?",
            (score, total_questions, quiz_result_id)
        )
        conn.commit()
    finally:
        conn.close()

def list_skill_tests():
    """List all skill tests."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skill_tests;")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_skill_test_questions(skill_test_id: int, limit: int = 10):
    """Get the questions for a skill test."""
    if not skill_test_id:
        raise ValueError("Skill test ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE skill_test_id = ? LIMIT ?", (skill_test_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def record_user_answer(session_id: int, question_id: int, user_answer: str, is_correct: bool):
    """Record or update a user's answer for a question within a quiz result."""
    if not session_id or not question_id:
        raise ValueError("Session ID and question ID are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM quiz_result_questions WHERE quiz_result_id = ? AND question_id = ?",
            (session_id, question_id)
        )
        # Insert new answer
        cursor.execute(
            "INSERT INTO quiz_result_questions (quiz_result_id, question_id, user_answer, is_correct) VALUES (?, ?, ?, ?)",
            (session_id, question_id, user_answer, 1 if is_correct else 0)
        )
        conn.commit()
    finally:
        conn.close()

def update_question_stats(question_id: int, correct_answers: int, incorrect_answers: int):
    """Update the question stats for a question."""
    if not question_id:
        raise ValueError("Question ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE questions SET correct_answers = ?, incorrect_answers = ? WHERE id = ?",
            (correct_answers, incorrect_answers, question_id)
        )
        conn.commit()
    finally:
        conn.close()

def update_user_skill_stats(user_id: int, skill_test_id: int, correct_answers: int, incorrect_answers: int):
    """Update the user skill stats for a skill test."""
    if not user_id or not skill_test_id:
        raise ValueError("User ID and skill test ID are required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE user_skill_stats SET correct_answers = ?, incorrect_answers = ? WHERE user_id = ? AND skill_test_id = ?",
            (correct_answers, incorrect_answers, user_id, skill_test_id)
        )
        conn.commit()
    finally:
        conn.close()

def get_quiz_session(session_id: int):
    """Get a quiz session by session ID."""
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
    """Get the history of quiz sessions for a user."""
    if not user_id:
        raise ValueError("User ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_results WHERE user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_skill_test_leaderboard(skill_test_id: int):
    """Get the leaderboard for a skill test."""
    if not skill_test_id:
        raise ValueError("Skill test ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_results WHERE skill_test_id = ? ORDER BY score DESC", (skill_test_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_user_performance(user_id: int):
    """Get the performance of a user across all skill tests."""
    if not user_id:
        raise ValueError("User ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_skill_stats WHERE user_id = ?", (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_correct_answers(quiz_result_id: int):
    """Get the correct answers for a quiz session."""
    if not quiz_result_id:
        raise ValueError("Session ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_result_questions WHERE quiz_result_id = ? AND is_correct = 1", (quiz_result_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_incorrect_answers(quiz_result_id: int):
    """Get all incorrect answers for a quiz session."""
    if not quiz_result_id:
        raise ValueError("Session ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_result_questions WHERE quiz_result_id = ? AND is_correct = 0", (quiz_result_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_all_answers_with_questions(quiz_result_id: int):
    """Get all answers for a quiz session with question details. Returns a list of answer dictionaries with question info."""
    if not quiz_result_id:
        raise ValueError("Session ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                qrq.id,
                qrq.quiz_result_id,
                qrq.question_id,
                qrq.user_answer,
                qrq.is_correct,
                q.id as q_id,
                q.prompt,
                q.answer as correct_answer,
                q.category
            FROM quiz_result_questions qrq
            JOIN questions q ON qrq.question_id = q.id
            WHERE qrq.quiz_result_id = ?
            ORDER BY qrq.question_id ASC
            """,
            (quiz_result_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_study_guide_by_skill_test(skill_test_id: int):
    """Get study guide content for a skill test."""
    if not skill_test_id:
        raise ValueError("Skill test ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_guides WHERE skill_test_id = ? ORDER BY id ASC", (skill_test_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_leaderboard_by_skill_test(skill_test_id: int, limit: int = 10):
    """Get leaderboard for a skill test with user information."""
    if not skill_test_id:
        raise ValueError("Skill test ID is required")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT qr.id, qr.score, qr.total_questions, qr.start_time, qr.end_time, u.username, st.name as skill_test_name
            FROM quiz_results qr
            JOIN users u ON qr.user_id = u.id
            JOIN skill_tests st ON qr.skill_test_id = st.id
            WHERE qr.skill_test_id = ? AND qr.end_time > qr.start_time
            ORDER BY qr.score DESC, qr.end_time ASC
            LIMIT ?""",
            (skill_test_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()
