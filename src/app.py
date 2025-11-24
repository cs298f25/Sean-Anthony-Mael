from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask import session as flask_session
import os
import sys
import sqlite3
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.database import init_database, create_user, get_user, login_user
from services import (
    start_quiz_service, submit_answer_service, finish_quiz_service,
    get_quiz_data_service, get_user_quiz_history_service,
    get_all_answers_with_questions_service,
    get_study_guide_service, get_leaderboard_service 
)
from database.db_services import list_skill_tests

# Configure Flask to use frontend folder for templates and static files
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_url_path=''
)
init_database()
# Set secret key for sessions (fallback to a dev default for local use)
app.secret_key = os.getenv('FLASK_KEY') or 'dev-secret-key' 

@app.after_request
def add_cors_headers(response):
    """Allow cross-origin requests for local development (e.g., when UI runs on a different port)."""
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - serves index.html with skill tests from database."""
    return render_template('index.html', skill_tests=list_skill_tests())

@app.route('/api/register', methods=['POST'])
def api_register():
    """Register a new user with username and password."""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400

    try:
        user_id = create_user(username, password)
        user = get_user(username)
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists.'}), 409
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    flask_session['user_id'] = user_id
    flask_session['username'] = username

    return jsonify({
        'user': {
            'id': user_id,
            'username': user['username'],
            'created_at': user['created_at'],
            'updated_at': user['updated_at']
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def api_login():
    """Authenticate an existing user."""
    data = request.get_json(silent=True) or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400

    try:
        user = login_user(username, password)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    if user is None:
        return jsonify({'error': 'Invalid credentials.'}), 401

    flask_session['user_id'] = user['id']
    flask_session['username'] = user['username']

    return jsonify({
        'user': {
            'id': user['id'],
            'username': user['username'],
            'created_at': user['created_at'],
            'updated_at': user['updated_at']
        }
    })

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Clear the user session."""
    flask_session.pop('user_id', None)
    flask_session.pop('username', None)
    return jsonify({'status': 'logged_out'})

@app.route('/quiz/start', methods=['POST'])
def start_quiz():
    """Handle quiz start form submission."""
    username = request.form.get('username', '').strip()
    skill_test_id = request.form.get('skill_test_id', '').strip()
    
    if not username or not skill_test_id:
        return redirect(url_for('index'))
    
    try:
        quiz_data = start_quiz_service(username, int(skill_test_id))
        if not quiz_data.get('questions'):
            return redirect(url_for('index'))
        
        flask_session.update({
            'quiz_session_id': quiz_data['session_id'],
            'username': username,
            'questions': quiz_data['questions'],
            'current_question_index': 0,
            'answers': {}
        })
        return redirect(url_for('quiz_page', session_id=quiz_data['session_id']))
    except (ValueError, KeyError):
        return redirect(url_for('index'))

def _get_skill_test(skill_test_id):
    """Helper to get skill test by ID."""
    return next((st for st in list_skill_tests() if st.get('id') == skill_test_id), None)

@app.route('/quiz/<int:session_id>')
def quiz_page(session_id):
    """Display quiz questions page."""
    # Verify session_id matches stored session
    if flask_session.get('quiz_session_id') != session_id:
        return redirect(url_for('index'))
    
    questions = flask_session.get('questions', [])
    if not questions:
        return redirect(url_for('index'))

    current_index = max(0, min(flask_session.get('current_question_index', 0), len(questions) - 1))
    direction = request.args.get('direction')
    
    if direction == 'prev' and current_index > 0:
        current_index -= 1
    elif direction == 'next' and current_index < len(questions) - 1:
        current_index += 1
    
    flask_session['current_question_index'] = current_index
    current_question = questions[current_index]
    # Parse choices JSON if it's a multiple choice question
    if current_question.get('question_type') == 'multiple_choice' and current_question.get('choices'):
        if isinstance(current_question['choices'], str):
            try:
                current_question['choices'] = json.loads(current_question['choices'])
            except (json.JSONDecodeError, TypeError):
                current_question['choices'] = []
    quiz_data = get_quiz_data_service(session_id)
    answers = flask_session.get('answers', {})
    
    return render_template('quiz.html', 
                    session_id=session_id,
                    current_question=current_question,
                    question_number=current_index + 1,
                    total_questions=len(questions),
                    quiz_data=quiz_data,
                    current_answer=answers.get(str(current_question.get('id')), ''),
                    skill_test=_get_skill_test(quiz_data.get('skill_test_id')) if quiz_data else None)

@app.route('/quiz/submit', methods=['POST'])
def submit_answer():
    """Handle answer submission."""
    try:
        session_id = int(request.form.get('session_id', 0))
        question_id = int(request.form.get('question_id', 0))
        user_answer = request.form.get('answer', '').strip()
        correct_answer = request.form.get('correct_answer', '').strip()
        
        if not all([session_id, question_id, user_answer, correct_answer]):
            return redirect(url_for('quiz_page', session_id=session_id))
        
        if flask_session.get('quiz_session_id') != session_id:
            return redirect(url_for('index'))
        
        questions = flask_session.get('questions', [])
        current_index = flask_session.get('current_question_index', 0)
        
        if not questions or current_index >= len(questions):
            return redirect(url_for('index'))
        
        # Verify we're answering the current question
        if questions[current_index].get('id') != question_id:
            return redirect(url_for('quiz_page', session_id=session_id))
        
        # Store answer
        answers = flask_session.get('answers', {})
        answers[str(question_id)] = user_answer
        flask_session['answers'] = answers
        
        # Get question type for answer validation
        question_type = questions[current_index].get('question_type', 'text_input')
        
        # Save to database (continue on error)
        try:
            submit_answer_service(session_id, question_id, user_answer, correct_answer, question_type)
        except Exception:
            pass
        
        # Move to next question if available
        next_index = current_index + 1
        flask_session['current_question_index'] = min(next_index, len(questions) - 1)
        return redirect(url_for('quiz_page', session_id=session_id))
    except (ValueError, KeyError):
        return redirect(url_for('index'))

@app.route('/quiz/<int:session_id>/finish', methods=['POST'])
def finish_quiz(session_id):
    """Finish quiz and show results."""
    # Save final answer if provided
    question_id = request.form.get('question_id')
    user_answer = request.form.get('answer', '').strip()
    correct_answer = request.form.get('correct_answer', '').strip()
    
    if question_id and user_answer and correct_answer:
        try:
            question_id_int = int(question_id)
            answers = flask_session.get('answers', {})
            answers[str(question_id_int)] = user_answer
            flask_session['answers'] = answers
            # Get question type from current question
            questions = flask_session.get('questions', [])
            current_question = next((q for q in questions if q.get('id') == question_id_int), None)
            question_type = current_question.get('question_type', 'text_input') if current_question else 'text_input'
            try:
                submit_answer_service(session_id, question_id_int, user_answer, correct_answer, question_type)
            except Exception:
                pass
        except ValueError:
            pass
    
    # Verify all questions answered
    questions = flask_session.get('questions', [])
    answers = flask_session.get('answers', {})
    
    if not questions:
        return redirect(url_for('index'))
    
    unanswered = [idx for idx, q in enumerate(questions) if str(q.get('id')) not in answers]
    if unanswered:
        flask_session['current_question_index'] = unanswered[0]
        return redirect(url_for('quiz_page', session_id=session_id))
    
    # Finish quiz
    results = finish_quiz_service(session_id)
    if not results:
        return redirect(url_for('index'))
    
    # Clear session
    for key in ['quiz_session_id', 'questions', 'current_question_index', 'answers']:
        flask_session.pop(key, None)
    
    return redirect(url_for('show_results', session_id=session_id))

@app.route('/results/<int:session_id>')
def show_results(session_id):
    """Display quiz results."""
    quiz_data = get_quiz_data_service(session_id)
    if not quiz_data:
        return redirect(url_for('index'))
    
    results = finish_quiz_service(session_id)
    if not results:
        return redirect(url_for('index'))
    
    all_answers = get_all_answers_with_questions_service(session_id)
    # Parse choices JSON for multiple choice questions in results
    for answer in all_answers:
        if answer.get('question_type') == 'multiple_choice' and answer.get('choices'):
            if isinstance(answer['choices'], str):
                try:
                    answer['choices'] = json.loads(answer['choices'])
                except (json.JSONDecodeError, TypeError):
                    answer['choices'] = []
    
    return render_template('results.html', 
                        session_id=session_id,
                        results=results,
                        quiz_data=quiz_data,
                        all_answers=all_answers,
                        skill_test=_get_skill_test(quiz_data.get('skill_test_id')))

@app.route('/history/<username>')
def user_history(username):
    """Show user's quiz history."""
    history = get_user_quiz_history_service(username)
    return render_template('history.html', 
                        username=username, 
                        history=history)

@app.route('/preview/<int:skill_test_id>')
def preview_skill_test(skill_test_id):
    """Preview page showing leaderboard and study guide for a skill test."""
    skill_test = _get_skill_test(skill_test_id)
    if not skill_test:
        return redirect(url_for('index'))
    
    return render_template('preview.html', 
                        skill_test=skill_test,
                        leaderboard=get_leaderboard_service(skill_test_id, limit=10),
                        study_guide=get_study_guide_service(skill_test_id),
                        username=flask_session.get('username', ''))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
