from flask import Flask, request, jsonify
import os
import html

app = Flask(__name__)
LOG_FILE = 'logs.txt'

# Set file permissions for logs.txt
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w'):
        pass
    os.chmod(LOG_FILE, 0o600)  # Read/write for owner only

@app.route('/log', methods=['POST'])
def log_message():
    data = request.get_json()
    if 'message' not in data:
        return jsonify({'error': 'Message field is required'}), 400
    
    message = html.escape(data['message'])  # Sanitize the message
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(message + '\n')
    except Exception as e:
        return jsonify({'error': 'Failed to write log message'}), 500
    
    return jsonify({'status': 'Log message successful'}), 200

@app.route('/logs', methods=['GET'])
def get_logs():
    try:
        with open(LOG_FILE, 'r') as f:
            logs = f.read()
    except FileNotFoundError:
        logs = ''
    except Exception as e:
        return jsonify({'error': 'Failed to read log messages'}), 500
    
    return logs, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)