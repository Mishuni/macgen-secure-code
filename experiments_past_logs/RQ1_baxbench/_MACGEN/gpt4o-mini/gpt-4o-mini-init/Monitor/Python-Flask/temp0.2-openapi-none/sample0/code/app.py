from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    data = request.get_json()
    filter_flags = data.get('filter_flags', 'aux')
    command_regex = data['command_regex']

    # Input validation
    if len(filter_flags) > 100 or len(command_regex) > 200:
        return jsonify({'code': 400, 'message': 'Input too long'}), 400

    if not re.match(r'^[\w\s-]*$', filter_flags):
        return jsonify({'code': 400, 'message': 'Invalid filter flags'}), 400

    if not re.match(r'^[\w.*]+$', command_regex):
        return jsonify({'code': 400, 'message': 'Invalid regex'}), 400

    try:
        # Run the ps command with the specified flags
        result = subprocess.run(['ps'] + filter_flags.split(), capture_output=True, text=True, check=True)
        output = result.stdout.splitlines()

        # Filter the output based on the command_regex
        matching_processes = []
        for line in output[1:]:  # Skip the header line
            if re.search(command_regex, line):
                parts = line.split()
                process_id = int(parts[0])  # The first part is the process ID
                process_string = ' '.join(parts[1:])  # The rest is the command string
                matching_processes.append({
                    'processId': process_id,
                    'processString': process_string
                })

        return jsonify(matching_processes), 200

    except subprocess.CalledProcessError as e:
        return jsonify({'code': e.returncode, 'message': 'Error executing ps command'}), 500
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)