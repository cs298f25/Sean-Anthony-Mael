from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({'message': 'Welcome to the Flask server'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
