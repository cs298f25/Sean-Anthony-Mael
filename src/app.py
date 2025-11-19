from flask import Flask, jsonify, request, send_from_directory, send_file, session
from dotenv import load_dotenv
import os
import sys
from pathlib import Path
from weather import fetch_weather
# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from database import services
from database.database import init_database
import ai_chat_controller

load_dotenv()

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')

app.secret_key = os.getenv("FLASK_KEY")

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

# Serve frontend for all other routes
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


# User endpoints
@app.route('/api/users', methods=['POST'])
def create_user_endpoint():
    """Create a new user."""
    try:
        data = request.get_json() or {}
        name = data.get('name')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        user_id = services.create_user(name=name, latitude=latitude, longitude=longitude)
        user = services.get_user(user_id)
        return jsonify({'user_id': user_id, 'user': dict(user)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_endpoint(user_id):
    """Get user by user_id."""
    try:
        user = services.get_user(user_id)
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
        
        services.update_user_location(user_id, latitude, longitude)
        user = services.get_user(user_id)
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
        
        services.update_user_name(user_id, name)
        user = services.get_user(user_id)
        if user:
            return jsonify(dict(user))
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/visit', methods=['PUT'])
def update_user_visit_endpoint(user_id):
    """Update user's last_updated timestamp on visit."""
    try:
        services.update_user_visit(user_id)
        user = services.get_user(user_id)
        if user:
            return jsonify(dict(user))
        return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/artists/by-genre/<string:genre_name>', methods=['GET'])
def get_artists_by_genre_endpoint(genre_name: str):
    """
    On-demand endpoint. Fetches artists from Last.fm,
    stores them, and returns them from our DB.
    """
    try:
        artists = services.fetch_and_store_artists_by_genre(genre_name)
        return jsonify(artists)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tracks/by-artist/<int:artist_id>', methods=['GET'])
def get_tracks_by_artist_endpoint(artist_id: int):
    """
    On-demand endpoint. Fetches tracks, stores them,
    and returns them.
    """
    try:
        artist_name = request.args.get('name')
        if not artist_name:
            return jsonify({'error': 'Artist name is required as a query parameter (?name=...)'}), 400
            
        tracks = services.fetch_and_store_tracks_by_artist(artist_id, artist_name)
        return jsonify(tracks)
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
    """Chat with AI, using session for history and tool use."""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get history from session, or start a new one
        messages_history = session.get('chat_history', [])
        
        # Run the controller logic
        final_response, updated_history = ai_chat_controller.handle_chat_message(
            user_message, 
            messages_history
        )
        
        # Save the updated history back to the session
        session['chat_history'] = updated_history
        
        return jsonify({'response': final_response})
    
    except Exception as e:
        # This will catch errors from the AI, network, etc.
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
