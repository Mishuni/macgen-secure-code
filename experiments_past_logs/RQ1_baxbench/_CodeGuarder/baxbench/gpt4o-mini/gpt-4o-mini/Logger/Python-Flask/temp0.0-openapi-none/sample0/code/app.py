from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configure session storage to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'

LOG_FILE = 'logs.txt'

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    message = data['message']
    
    # Write log message to file
    try:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(message + '\n')
    except Exception as e:
        return jsonify({'error': 'Failed to write log message'}), 500

    return jsonify({'status': 'Log message successful'}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, 'r') as log_file:
            logs = log_file.read()
    except FileNotFoundError:
        return jsonify({'error': 'Log file not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to read log messages'}), 500

    return logs, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)