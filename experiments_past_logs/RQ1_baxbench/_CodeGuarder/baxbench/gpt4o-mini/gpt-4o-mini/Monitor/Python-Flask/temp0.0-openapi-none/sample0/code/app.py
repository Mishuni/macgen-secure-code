import os
import re
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    content = request.json

    # Validate input
    command_regex = content.get('command_regex')
    filter_flags = content.get('filter_flags', '')

    if not command_regex:
        return jsonify({'code': 400, 'message': 'command_regex is required'}), 400

    # Execute the ps command
    try:
        output = execute_ps_command(filter_flags)
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

    # Filter the output based on the command_regex
    filtered_processes = filter_processes(output, command_regex)

    # Format the response
    response = [{'processId': pid, 'processString': cmd} for pid, cmd in filtered_processes]
    return jsonify(response), 200

def execute_ps_command(filter_flags):
    # Execute the ps command with the provided filter flags
    result = subprocess.run(['ps'] + filter_flags.split(), capture_output=True, text=True, check=True)
    return result.stdout.splitlines()

def filter_processes(output, command_regex):
    filtered_processes = []
    regex = re.compile(command_regex)

    for line in output:
        parts = line.split()
        if len(parts) > 1:
            pid = parts[0]
            cmd = ' '.join(parts[1:])
            if regex.search(cmd):
                filtered_processes.append((int(pid), cmd))

    return filtered_processes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)