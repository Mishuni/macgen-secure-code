from flask import Flask, request, jsonify, abort
import os
import re
from logging.handlers import RotatingFileHandler
import logging

app = Flask(__name__)

LOG_FILE = "logs.txt"

# Configure logging with rotation and secure file permissions
handler = RotatingFileHandler(LOG_FILE, maxBytes=10000, backupCount=5)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)

# Ensure log file has secure permissions
os.chmod(LOG_FILE, 0o600)

def sanitize_input(input_string):
    # Improved sanitization to remove potentially harmful characters
    return re.sub(r'[^\w\s]', '', input_string)

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input"}), 400

    message = sanitize_input(data['message'])
    # Avoid logging sensitive information
    app.logger.info("Received a log message")

    return jsonify({"status": "Log message successful"}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    abort(403)  # Disable direct access to logs for security reasons

if __name__ == '__main__':
    # Run the application with the least privileges necessary
    app.run(host='0.0.0.0', port=5000, debug=False)