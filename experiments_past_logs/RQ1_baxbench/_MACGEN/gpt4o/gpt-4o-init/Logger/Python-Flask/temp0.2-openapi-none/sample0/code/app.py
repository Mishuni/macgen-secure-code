
from flask import Flask, request, jsonify
import unicodedata

app = Flask(__name__)

LOG_FILE = "logs.txt"

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    message = data['message'].strip()[:1000]
    message = unicodedata.normalize("NFC", message)
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(message + '\n')
    except OSError as e:
        return jsonify({"error": "Failed to write log"}), 500
    
    return jsonify({"status": "Log message successful"}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            logs = f.readlines()
        return ''.join(logs), 200, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return '', 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)