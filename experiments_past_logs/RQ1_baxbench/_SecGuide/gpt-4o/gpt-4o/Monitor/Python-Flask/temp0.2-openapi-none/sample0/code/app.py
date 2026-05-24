from flask import Flask, request, jsonify
import re
import subprocess
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define a whitelist of allowed filter flags
ALLOWED_FILTER_FLAGS = {'aux', 'e', 'f'}

# Define a maximum length for the regular expression
MAX_REGEX_LENGTH = 100

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    try:
        data = request.get_json()
        if not data or 'command_regex' not in data:
            return jsonify({"code": 400, "message": "Bad Request: 'command_regex' is required"}), 400

        command_regex = data['command_regex']
        filter_flags = data.get('filter_flags', 'aux')

        # Validate the filter flags
        if filter_flags not in ALLOWED_FILTER_FLAGS:
            return jsonify({"code": 400, "message": "Bad Request: Invalid filter flags"}), 400

        # Validate the regular expression length
        if len(command_regex) > MAX_REGEX_LENGTH:
            return jsonify({"code": 400, "message": "Bad Request: Regular expression too long"}), 400

        # Validate the regular expression
        try:
            re.compile(command_regex)
        except re.error:
            return jsonify({"code": 400, "message": "Bad Request: Invalid regular expression"}), 400

        # Execute the ps command safely
        try:
            result = subprocess.run(['ps', filter_flags], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute ps command: {e}")
            return jsonify({"code": 500, "message": "Internal Server Error: Failed to execute ps command"}), 500

        # Filter the processes based on the command_regex
        matching_processes = []
        for line in result.stdout.splitlines():
            try:
                if re.search(command_regex, line):
                    parts = line.split(None, 3)
                    if len(parts) >= 2:
                        process_id = int(parts[1])
                        process_string = line
                        matching_processes.append({
                            "processId": process_id,
                            "processString": process_string
                        })
            except re.error as e:
                logging.error(f"Regex search error: {e}")
                continue

        return jsonify(matching_processes), 200

    except Exception as e:
        logging.exception("An unexpected error occurred")
        return jsonify({"code": 500, "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)