from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from weather import fetch_weather

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.route('/weather', methods=['GET'])
def get_weather():
    try:
        result = fetch_weather()
        return jsonify(result)
    except Exception as e:
        # Keep messages generic; specifics are handled/logged in the weather module
        message = str(e) or 'Failed to fetch weather'
        # Return 500 by default; upstream errors may warrant 502 in extended handling
        return jsonify({'error': message}), 500


if __name__ == '__main__':
    app.run(port=8000, debug=True)


