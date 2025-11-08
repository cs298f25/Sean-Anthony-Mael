from flask import Flask, jsonify, request, send_from_directory, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from weather import fetch_weather
from ai_chat import chat_with_ai
from database import (
    init_database, create_user, get_user, update_user_location, update_user_name,
    add_music, get_music, get_all_music, update_music, delete_music
)

load_dotenv()

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
CORS(app)

# Initialize database on startup
init_database()

# Helper function to get frontend dist path
def get_frontend_dist_path():
    return os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist')

# Serve React app for all non-API routes
@app.route('/')
def index():
    dist_path = get_frontend_dist_path()
    index_path = os.path.join(dist_path, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        return jsonify({'error': 'Frontend not built. Please run "npm run build" in the frontend directory.'}), 503

@app.route('/<path:path>')
def serve_frontend(path):
    # Don't serve API routes through this handler
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    dist_path = get_frontend_dist_path()
    file_path = os.path.join(dist_path, path)
    
    # Serve static files if they exist
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(dist_path, path)
    
    # Otherwise serve index.html for client-side routing
    index_path = os.path.join(dist_path, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        return jsonify({'error': 'Frontend not built. Please run "npm run build" in the frontend directory.'}), 503


# API Routes

# User endpoints
@app.route('/api/users', methods=['POST'])
def create_user_endpoint():
    """Create a new user."""
    try:
        data = request.get_json() or {}
        name = data.get('name')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        user_id = create_user(name=name, latitude=latitude, longitude=longitude)
        user = get_user(user_id)
        return jsonify({'user_id': user_id, 'user': dict(user)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_endpoint(user_id):
    """Get user by user_id."""
    try:
        user = get_user(user_id)
        if user:
            return jsonify(dict(user))
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/location', methods=['PUT'])
def update_user_location_endpoint(user_id):
    """Update user's location."""
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'latitude and longitude are required'}), 400
        
        update_user_location(user_id, latitude, longitude)
        user = get_user(user_id)
        if user:
            return jsonify(dict(user))
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/name', methods=['PUT'])
def update_user_name_endpoint(user_id):
    """Update user's name."""
    try:
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({'error': 'name is required'}), 400
        
        update_user_name(user_id, name)
        user = get_user(user_id)
        if user:
            return jsonify(dict(user))
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Music endpoints
@app.route('/api/music', methods=['POST'])
def add_music_endpoint():
    """Add a new music entry."""
    try:
        data = request.get_json()
        title = data.get('title')
        
        if not title:
            return jsonify({'error': 'title is required'}), 400
        
        music_id = add_music(
            title=title,
            artist=data.get('artist'),
            album=data.get('album'),
            genre=data.get('genre'),
            year=data.get('year'),
            duration=data.get('duration'),
            file_path=data.get('file_path'),
            metadata=data.get('metadata')
        )
        music = get_music(music_id)
        return jsonify({'music_id': music_id, 'music': dict(music)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music', methods=['GET'])
def get_all_music_endpoint():
    """Get all music entries."""
    try:
        music_list = get_all_music()
        return jsonify({'music': music_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/<int:music_id>', methods=['GET'])
def get_music_endpoint(music_id):
    """Get music by music_id."""
    try:
        music = get_music(music_id)
        if music:
            return jsonify(dict(music))
        return jsonify({'error': 'Music not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/<int:music_id>', methods=['PUT'])
def update_music_endpoint(music_id):
    """Update music entry."""
    try:
        data = request.get_json() or {}
        updated = update_music(music_id, **data)
        
        if updated:
            music = get_music(music_id)
            return jsonify(dict(music))
        return jsonify({'error': 'Music not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/music/<int:music_id>', methods=['DELETE'])
def delete_music_endpoint(music_id):
    """Delete music entry."""
    try:
        deleted = delete_music(music_id)
        if deleted:
            return jsonify({'message': 'Music deleted successfully'})
        return jsonify({'error': 'Music not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Feature endpoints
@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather information."""
    try:
        result = fetch_weather()
        return jsonify(result)
    except Exception as e:
        message = str(e) or 'Failed to fetch weather'
        return jsonify({'error': message}), 500

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat with AI."""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id')  # Optional: track which user is chatting
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        ai_response = chat_with_ai(user_message)
        return jsonify({'response': ai_response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
