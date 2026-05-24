from flask import Flask, request, jsonify
import subprocess
import re
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    data = request.get_json()

    # Validate input
    if 'command_regex' not in data:
        return jsonify({"code": 400, "message": "command_regex is required"}), 400

    # Validate filter_flags to only allow safe values
    allowed_flags = {'aux', 'e', 'f', 'l', 'm', 'o', 'p', 't', 'u', 'x'}
    filter_flags = data.get('filter_flags', 'aux')
    if filter_flags not in allowed_flags:
        return jsonify({"code": 400, "message": "Invalid filter_flags value"}), 400

    command_regex = data['command_regex']
    
    # Validate command_regex to prevent excessive backtracking
    try:
        re.compile(command_regex)
    except re.error:
        return jsonify({"code": 400, "message": "Invalid command_regex"}), 400

    try:
        # Execute the ps command with the provided filter flags
        result = subprocess.run(['ps', filter_flags], capture_output=True, text=True, check=True)
        processes = result.stdout.splitlines()

        matching_processes = []
        for process in processes[1:]:  # Skip the header line
            if re.search(command_regex, process):
                parts = process.split()
                process_id = int(parts[1])  # Assuming the second column is the PID
                matching_processes.append({
                    "processId": process_id,
                    "processString": process
                })

        return jsonify(matching_processes), 200

    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e}")
        return jsonify({"code": 500, "message": "Error executing command"}), 500
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"code": 500, "message": "An error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)