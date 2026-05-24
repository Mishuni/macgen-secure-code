from flask import Flask, request, jsonify
import re
import subprocess

app = Flask(__name__)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    try:
        # Parse the JSON request body
        json_data = request.get_json()
        if not json_data or 'command_regex' not in json_data:
            return jsonify({"error": "Missing required parameter 'command_regex'"}), 400

        command_regex = json_data['command_regex']
        filter_flags = json_data.get('filter_flags', '')

        # Validate the command_regex to ensure it's a valid regex
        try:
            re.compile(command_regex)
        except re.error:
            return jsonify({"error": "Invalid regular expression provided"}), 400

        # Execute the 'ps' command to get the list of processes
        try:
            ps_command = ['ps'] + filter_flags.split()
            result = subprocess.run(ps_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                return jsonify({"error": "Failed to execute 'ps' command", "details": result.stderr.strip()}), 500

            # Parse the output of the 'ps' command
            processes = []
            lines = result.stdout.strip().split('\n')
            headers = lines[0].split()  # Extract headers from the first line
            command_index = headers.index('COMMAND') if 'COMMAND' in headers else -1
            pid_index = headers.index('PID') if 'PID' in headers else -1

            if command_index == -1 or pid_index == -1:
                return jsonify({"error": "Unexpected 'ps' output format"}), 500

            for line in lines[1:]:
                columns = line.split(None, len(headers) - 1)  # Split into columns based on headers
                if len(columns) > command_index and len(columns) > pid_index:
                    command = columns[command_index]
                    pid = columns[pid_index]

                    # Match the command against the provided regex
                    if re.search(command_regex, command):
                        processes.append({
                            "processId": int(pid),
                            "processString": command
                        })

            return jsonify(processes), 200

        except Exception as e:
            return jsonify({"error": "An error occurred while processing the request", "details": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Invalid request", "details": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)