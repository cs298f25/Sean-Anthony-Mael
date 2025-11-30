import json
from database.db_services import (
    start_quiz_session, finish_quiz_session,
    get_skill_test_questions, record_user_answer, get_quiz_session,
    update_question_stats, get_correct_answers, get_incorrect_answers,
    get_all_answers_with_questions, get_study_guide_by_skill_test, get_leaderboard_by_skill_test
)
from database.database import create_user, get_user

def start_quiz_service(username: str, skill_test_id: int):
    """Start a new quiz session for a user. Returns session data with questions."""
    user = get_user(username) or get_user(create_user(username))
    questions = get_skill_test_questions(skill_test_id, limit=10)
    # Parse choices JSON for multiple choice questions
    for question in questions:
        if question.get('question_type') == 'multiple_choice' and question.get('choices'):
            try:
                question['choices'] = json.loads(question['choices'])
            except (json.JSONDecodeError, TypeError):
                question['choices'] = []
    return {
        'session_id': start_quiz_session(user['id'], skill_test_id, len(questions)),
        'questions': questions
    }

def submit_answer_service(session_id: int, question_id: int, user_answer: str, correct_answer: str, question_type: str = 'text_input'):
    """Submit an answer and record if it's correct."""
    is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
    record_user_answer(session_id, question_id, user_answer, is_correct)
    update_question_stats(question_id, int(is_correct), int(not is_correct))
    return is_correct

def finish_quiz_service(session_id: int):
    """Finish a quiz session and calculate the score."""
    session = get_quiz_session(session_id)
    if not session:
        return None
    
    correct_answers = get_correct_answers(session_id)
    incorrect_answers = get_incorrect_answers(session_id)
    total_answered = len(correct_answers) + len(incorrect_answers)
    
    if total_answered == 0:
        return None
    
    correct_count = len(correct_answers)
    score = (correct_count / total_answered) * 100
    
    finish_quiz_session(session_id, score, total_answered)
    
    return {
        'session_id': session_id,
        'score': score,
        'total_questions': total_answered,
        'correct_count': correct_count,
        'incorrect_count': len(incorrect_answers)
    }

def get_quiz_data_service(session_id: int):
    """Get quiz session data for display."""
    return get_quiz_session(session_id)

def get_study_guide_service(skill_test_id: int):
    """Get study guide content for a skill test."""
    return get_study_guide_by_skill_test(skill_test_id)

def get_leaderboard_service(skill_test_id: int, limit: int = 10):
    """Get leaderboard for a skill test with user info."""
    return get_leaderboard_by_skill_test(skill_test_id, limit)

def get_all_answers_with_questions_service(session_id: int):
    """Get all answers for a quiz session with question details."""
    return get_all_answers_with_questions(session_id)