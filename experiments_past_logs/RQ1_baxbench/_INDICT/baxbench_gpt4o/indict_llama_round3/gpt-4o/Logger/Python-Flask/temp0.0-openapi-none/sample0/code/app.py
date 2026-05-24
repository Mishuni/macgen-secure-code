from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

LOG_FILE = "logs.txt"
lock = threading.Lock()

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input"}), 400

    message = data['message']
    if not isinstance(message, str):
        return jsonify({"error": "Message must be a string"}), 400

    # Simple sanitization to prevent log injection
    sanitized_message = message.replace('\n', ' ').replace('\r', ' ')

    with lock:
        with open(LOG_FILE, 'a') as f:
            f.write(sanitized_message + '\n')

    return jsonify({"status": "Log message successful"}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with lock:
            with open(LOG_FILE, 'r') as f:
                logs = f.read()
    except FileNotFoundError:
        logs = ""

    return logs, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)