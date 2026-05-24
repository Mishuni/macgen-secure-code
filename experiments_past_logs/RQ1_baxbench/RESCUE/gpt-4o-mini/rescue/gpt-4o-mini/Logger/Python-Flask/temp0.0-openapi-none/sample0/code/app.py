from flask import Flask, request, jsonify
import os

app = Flask(__name__)
LOG_FILE = 'logs.txt'

@app.route('/log', methods=['POST'])
def log_message():
    json_data = request.get_json()
    if 'message' not in json_data or not json_data['message']:
        return jsonify({"msg": "Message is required"}), 400

    message = json_data['message']
    
    # Log the message to the file
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(message + '\n')

    return jsonify({"msg": "Log message successful"}), 200

@app.route('/logs', methods=['GET'])
def retrieve_logs():
    if not os.path.exists(LOG_FILE):
        return '', 200  # No logs available

    with open(LOG_FILE, 'r') as log_file:
        logs = log_file.read()

    return logs, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)