from flask import Flask
import os

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')

app.secret_key = os.getenv("FLASK_KEY")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
