from flask import Flask, request, jsonify
import os
import re
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
LOG_FILE = os.getenv('LOG_FILE', 'logs.txt')  # Use environment variable for log file path
LOG_DIR = os.path.dirname(LOG_FILE)

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

def sanitize_message(message):
    # Sanitize the message to prevent log injection
    return re.sub(r'[^\x20-\x7E]', '', message)  # Allow only printable ASCII characters

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    message = data['message']
    if not isinstance(message, str):
        return jsonify({'error': 'Message must be a string'}), 400

    # Validate message length
    if len(message) > 1024:  # Limit message length to 1024 characters
        return jsonify({'error': 'Message is too long'}), 400

    sanitized_message = sanitize_message(message)

    with open(LOG_FILE, 'a') as log_file:
        log_file.write(sanitized_message + '\n')

    return jsonify({'status': 'Log message successful'}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    if not os.path.exists(LOG_FILE):
        return '', 200

    with open(LOG_FILE, 'r') as log_file:
        logs = log_file.read()

    return logs, 200, {'Content-Type': 'text/plain'}

@app.errorhandler(HTTPException)
def handle_exception(e):
    # Log the error internally
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f'Error: {str(e)}\n')
    # Return a user-friendly error message
    return jsonify({'error': 'An error occurred'}), e.code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)