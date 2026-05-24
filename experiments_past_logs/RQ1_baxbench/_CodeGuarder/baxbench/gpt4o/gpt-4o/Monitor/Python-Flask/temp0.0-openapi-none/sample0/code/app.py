import os
import re
import subprocess
from flask import Flask, request, jsonify, abort

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    try:
        # Parse and validate request data
        if request.headers.get('content-type') != 'application/json':
            abort(400, description='Invalid content-type')

        data = request.get_json()
        if not data or 'command_regex' not in data:
            abort(400, description='Missing required fields')

        command_regex = data['command_regex']
        filter_flags = data.get('filter_flags', '')

        # Validate the regular expression
        try:
            re.compile(command_regex)
        except re.error:
            abort(400, description='Invalid regular expression')

        # Execute system command safely
        ps_command = ['ps'] + filter_flags.split()
        try:
            result = subprocess.run(ps_command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            abort(500, description='Error executing system command')

        # Filter processes using regex
        matching_processes = []
        for line in result.stdout.splitlines():
            if re.search(command_regex, line):
                parts = line.split(None, 3)
                if len(parts) >= 2:
                    process_id = int(parts[1])
                    process_string = line
                    matching_processes.append({'processId': process_id, 'processString': process_string})

        # Format and return response
        return jsonify(matching_processes), 200

    except Exception as exc:
        # Handle errors gracefully
        if app.debug:
            return jsonify({'error': str(exc)}), 500
        else:
            return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)