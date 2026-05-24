from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    json_data = request.get_json()
    
    # Validate input
    if 'command_regex' not in json_data:
        return jsonify({"code": 400, "message": "command_regex is required"}), 400
    
    command_regex = json_data['command_regex']
    filter_flags = json_data.get('filter_flags', '')

    # Construct the command
    command = ['ps'] + filter_flags.split() + ['-eo', 'pid,comm']
    
    try:
        # Execute the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Filter the output based on the regex
        process_list = []
        for line in output.splitlines()[1:]:  # Skip the header line
            match = re.match(r'(\d+)\s+(.+)', line)
            if match:
                pid = int(match.group(1))
                process_string = match.group(2)
                if re.search(command_regex, process_string):
                    process_list.append({"processId": pid, "processString": process_string})

        return jsonify(process_list), 200

    except subprocess.CalledProcessError as e:
        return jsonify({"code": 500, "message": "Error executing command"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)