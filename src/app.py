from flask import Flask, jsonify, render_template
import os

# Configure Flask to use frontend folder for templates and static files
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_url_path=''
)

@app.route('/')
def index():
    """Root endpoint - serves index.html."""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
