from flask import Flask, request, jsonify

app = Flask(__name__)
LOG_FILE = 'logs.txt'

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    
    if not isinstance(data, dict) or 'message' not in data:
        return jsonify({"error": "Invalid input, 'message' is required"}), 400
    
    message = data['message']
    
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message must be a non-empty string"}), 400
    
    try:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(message + '\n')
    except Exception:
        return jsonify({"error": "Failed to write log message"}), 500
    
    return jsonify({"message": "Log message successful"}), 200

@app.route('/logs', methods=['GET'])
def retrieve_logs():
    try:
        with open(LOG_FILE, 'r') as log_file:
            logs = log_file.read()
        return logs, 200, {'Content-Type': 'text/plain'}
    except FileNotFoundError:
        return '', 200, {'Content-Type': 'text/plain'}
    except Exception:
        return jsonify({"error": "Failed to read log messages"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)