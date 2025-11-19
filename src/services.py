from database.db_services import (
    create_user, get_user, start_quiz_session, finish_quiz_session,
    get_skill_test_questions, record_user_answer, get_quiz_session,
    update_question_stats, get_user_history, get_correct_answers, get_incorrect_answers,
    get_skill_test_leaderboard, get_user_performance
)
def start_quiz_service(username: str, skill_test_id: int):
    """Start a new quiz session for a user. Returns session data with questions."""
    # Ensure user exists
    user = get_user(username)
    if not user:
        create_user(username)
        user = get_user(username)
    
    # Start quiz session (creates session, selects 10 questions)
    session_id = start_quiz_session(user['id'], skill_test_id)
    
    # Get the 10 questions for this session
    questions = get_skill_test_questions(skill_test_id, limit=10)
    
    return {
        'session_id': session_id,
        'user_id': user['id'],
        'questions': questions
    }

def submit_answer_service(session_id: int, question_id: int, user_answer: str, correct_answer: str):
    """Submit an answer and record if it's correct."""
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    correct_count, incorrect_count = 0, 0
    if is_correct:
        correct_count += 1
    else:
        incorrect_count += 1
    
    # Record the answer in the database
    record_user_answer(session_id, question_id, user_answer, is_correct)
    
    # Update question statistics
    update_question_stats(question_id, correct_count, incorrect_count)
    
    return is_correct

def finish_quiz_service(session_id: int):
    """Finish a quiz session and calculate the score."""
    # Get session data

    session = get_quiz_session(session_id)
    if not session:
        return None
    
    # Calculate score from session answers
    correct_answers = get_correct_answers(session_id)
    incorrect_answers = get_incorrect_answers(session_id)
    score = len(correct_answers) / (len(correct_answers) + len(incorrect_answers)) * 100
    total_questions = 10
    
    # Finish the session
    finish_quiz_session(session_id, score, total_questions)
    
    return {
        'session_id': session_id,
        'score': score,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers
    }

def get_quiz_data_service(session_id: int):
    """Get quiz session data for display."""
    return get_quiz_session(session_id)

def get_user_quiz_history_service(username: str):
    """Get a user's quiz history."""
    user = get_user(username)
    if not user:
        return []
    
    history = get_user_history(user['id'])
    return history

def get_skill_test_leaderboard_service(skill_test_id: int):
    """Get the leaderboard for a skill test."""
    return get_skill_test_leaderboard(skill_test_id)

def get_user_performance_service(user_id: int):
    """Get the performance of a user across all skill tests."""
    return get_user_performance(user_id)

def get_correct_answers_service(session_id: int):
    """Get the correct answers for a quiz session."""
    return get_correct_answers(session_id)

def get_incorrect_answers_service(session_id: int):
    """Get the incorrect answers for a quiz session."""
    return get_incorrect_answers(session_id)