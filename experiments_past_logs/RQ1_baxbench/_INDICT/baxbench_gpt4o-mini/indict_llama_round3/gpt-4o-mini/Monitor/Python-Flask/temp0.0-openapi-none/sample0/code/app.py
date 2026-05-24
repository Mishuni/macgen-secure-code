from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    data = request.get_json()
    
    # Validate input
    if 'command_regex' not in data:
        return jsonify({"code": 400, "message": "command_regex is required"}), 400
    
    filter_flags = data.get('filter_flags', 'aux')
    
    # Validate filter_flags to prevent command injection
    if not re.match(r'^[a-zA-Z0-9\s-]*$', filter_flags):
        return jsonify({"code": 400, "message": "Invalid filter_flags"}), 400
    
    command_regex = data['command_regex']
    
    # Validate the regex pattern
    try:
        re.compile(command_regex)
    except re.error:
        return jsonify({"code": 400, "message": "Invalid command_regex"}), 400
    
    try:
        # Execute the ps command with the provided flags
        result = subprocess.run(['ps'] + filter_flags.split(), capture_output=True, text=True, check=True)
        processes = result.stdout.splitlines()
        
        matching_processes = []
        
        # Skip the header line
        for process in processes[1:]:
            # Match the process line against the regex
            if re.search(command_regex, process):
                parts = process.split()
                process_id = int(parts[0])  # Assuming the first part is the PID
                matching_processes.append({
                    "processId": process_id,
                    "processString": process
                })
        
        return jsonify(matching_processes), 200
    
    except subprocess.CalledProcessError:
        return jsonify({"code": 500, "message": "Error executing ps command"}), 500
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)