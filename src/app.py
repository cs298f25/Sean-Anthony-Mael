from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask import session as flask_session
import os
import sys
import sqlite3
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from database.database import init_database, create_user, get_user, login_user
from services import (
    start_quiz_service, submit_answer_service, finish_quiz_service,
    get_quiz_data_service, get_user_quiz_history_service,
    get_correct_answers_service, get_incorrect_answers_service,
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
    skill_tests = list_skill_tests()
    # Debug: print to see what we're getting
    print(f"Skill tests retrieved: {skill_tests}")
    return render_template('index.html', skill_tests=skill_tests or [])

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
        skill_test_id = int(skill_test_id)
        # Start quiz using service
        quiz_data = start_quiz_service(username, skill_test_id)
        
        # Store session_id in Flask session for tracking
        flask_session['quiz_session_id'] = quiz_data['session_id']
        flask_session['username'] = username
        flask_session['questions'] = quiz_data['questions']  # Store questions list
        flask_session['current_question_index'] = 0  # Start at first question
        
        # Redirect to quiz page with session_id
        return redirect(url_for('quiz_page', session_id=quiz_data['session_id']))
    except (ValueError, KeyError):
        return redirect(url_for('index'))

@app.route('/quiz/<int:session_id>')
def quiz_page(session_id):
    """Display quiz questions page."""
    # Verify session_id matches stored session
    if flask_session.get('quiz_session_id') != session_id:
        return redirect(url_for('index'))
    
    # Get current question index and questions from session
    current_index = flask_session.get('current_question_index', 0)
    questions = flask_session.get('questions', [])
    
    if not questions or current_index >= len(questions):
        return redirect(url_for('index'))
    
    # Get current question
    current_question = questions[current_index]
    quiz_data = get_quiz_data_service(session_id)

    return render_template('quiz.html', 
                    session_id=session_id,
                    current_question=current_question,
                    question_number=current_index + 1,
                    total_questions=len(questions),
                    quiz_data=quiz_data)

@app.route('/quiz/submit', methods=['POST'])
def submit_answer():
    """Handle answer submission."""
    session_id = request.form.get('session_id', '').strip()
    question_id = request.form.get('question_id', '').strip()
    user_answer = request.form.get('answer', '').strip()
    correct_answer = request.form.get('correct_answer', '').strip()
    
    if not all([question_id, user_answer, correct_answer]):
        return redirect(url_for('quiz_page', session_id=session_id))
    
    try:
        session_id = int(session_id)
        question_id = int(question_id)
        
        # Submit answer using service
        submit_answer_service(session_id, question_id, user_answer, correct_answer)
        
        # Get current question index and increment it
        current_index = flask_session.get('current_question_index', 0)
        questions = flask_session.get('questions', [])
        next_index = current_index + 1
        
        # Move to next question (or stay on last question if done)
        if next_index < len(questions):
            # More questions remaining, move to next
            flask_session['current_question_index'] = next_index
            return redirect(url_for('quiz_page', session_id=session_id))
        else:
            # All questions answered, stay on last question to show submit button
            flask_session['current_question_index'] = current_index  # Stay on last question
            return redirect(url_for('quiz_page', session_id=session_id))
            
    except ValueError:
        return redirect(url_for('index'))

@app.route('/quiz/<int:session_id>/finish', methods=['POST'])
def finish_quiz(session_id):
    """Finish quiz and show results. Only accessible via POST (button click)."""
    
    # Verify all questions have been answered
    current_index = flask_session.get('current_question_index', 0)
    questions = flask_session.get('questions', [])
    if current_index < len(questions) - 1:
        # Not all questions answered yet, redirect back to quiz
        return redirect(url_for('quiz_page', session_id=session_id))
    
    results = finish_quiz_service(session_id)
    
    if not results:
        return redirect(url_for('index'))
    
    # Clear quiz tracking from session (keep username)
    flask_session.pop('quiz_session_id', None)
    flask_session.pop('questions', None)
    flask_session.pop('current_question_index', None)
    
    return redirect(url_for('show_results', session_id=session_id))

@app.route('/results/<int:session_id>')
def show_results(session_id):
    """Display quiz results."""
    quiz_data = get_quiz_data_service(session_id)
    correct_answers = get_correct_answers_service(session_id)
    incorrect_answers = get_incorrect_answers_service(session_id)
    results = finish_quiz_service(session_id)
    
    if not quiz_data or not results:
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                        session_id=session_id,
                        results=results,
                        quiz_data=quiz_data,
                        correct_answers=correct_answers,
                        incorrect_answers=incorrect_answers)

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
    skill_tests = list_skill_tests()
    skill_test = next((st for st in skill_tests if st['id'] == skill_test_id), None)
    
    if not skill_test:
        return redirect(url_for('index'))
    
    leaderboard = get_leaderboard_service(skill_test_id, limit=10)
    study_guide = get_study_guide_service(skill_test_id)
    username = flask_session.get('username', '')
    
    return render_template('preview.html', 
                        skill_test=skill_test,
                        leaderboard=leaderboard,
                        study_guide=study_guide,
                        username=username)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
