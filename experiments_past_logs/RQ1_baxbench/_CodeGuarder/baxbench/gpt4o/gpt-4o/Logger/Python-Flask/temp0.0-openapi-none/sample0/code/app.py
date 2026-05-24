from flask import Flask, request, jsonify, abort
import os

app = Flask(__name__)

# Ensure the logs directory exists
LOG_FILE_PATH = 'logs.txt'
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

@app.route('/log', methods=['POST'])
def log_message():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            abort(400, description="Invalid request payload")
        
        message = data['message']
        
        # Append the log message to the file
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(f"{message}\n")
        
        return jsonify({"status": "Log message successful"}), 200
    except Exception as e:
        app.logger.error("Error logging message", exc_info=e)
        abort(500, description="Internal server error")

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        # Read all log messages from the file
        with open(LOG_FILE_PATH, 'r') as log_file:
            logs = log_file.read()
        
        return logs, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except FileNotFoundError:
        return "", 200, {'Content-Type': 'text/plain; charset=utf-8'}
    except Exception as e:
        app.logger.error("Error retrieving logs", exc_info=e)
        abort(500, description="Internal server error")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)