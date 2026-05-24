
from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    try:
        data = request.get_json()
        if not data or 'command_regex' not in data:
            return jsonify({"code": 400, "message": "Bad Request: 'command_regex' is required"}), 400

        filter_flags = data.get('filter_flags', 'aux')
        command_regex = data['command_regex']

        # Validate filter_flags
        allowed_flags = {'aux', 'x', '-T'}
        for flag in filter_flags.split():
            if flag not in allowed_flags:
                return jsonify({"code": 400, "message": "Bad Request: Invalid filter flags"}), 400

        # Validate command_regex length
        if len(command_regex) > 100:
            return jsonify({"code": 400, "message": "Bad Request: Regex too long"}), 400

        # Compile the regex
        try:
            compiled_regex = re.compile(command_regex)
        except re.error:
            return jsonify({"code": 400, "message": "Bad Request: Invalid regular expression"}), 400

        # Execute the ps command
        try:
            result = subprocess.run(['ps'] + filter_flags.split(), capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            return jsonify({"code": 500, "message": "Internal Server Error: Failed to execute ps command"}), 500

        # Process the output
        processes = []
        for line in result.stdout.splitlines():
            if compiled_regex.search(line):
                parts = line.split(None, 10)
                if len(parts) > 1:
                    process_id = parts[1]
                    process_string = line
                    processes.append({"processId": int(process_id), "processString": process_string})

        return jsonify(processes), 200

    except Exception:
        return jsonify({"code": 500, "message": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)