from flask import Flask, request, jsonify
import subprocess
import re

app = Flask(__name__)

@app.route('/monitor/commands', methods=['POST'])
def monitor_commands():
    data = request.get_json()
    
    if not data or 'command_regex' not in data:
        return jsonify({"code": 400, "message": "Bad Request: 'command_regex' is required"}), 400
    
    command_regex = data['command_regex']
    
    # Validate the command_regex to prevent ReDoS
    try:
        re.compile(command_regex)
    except re.error:
        return jsonify({"code": 400, "message": "Bad Request: Invalid regular expression"}), 400
    
    try:
        # Execute the ps command with safe flags
        result = subprocess.run(['ps', 'aux'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            return jsonify({"code": 500, "message": "Internal Server Error: Failed to execute ps command"}), 500
        
        # Filter the processes based on the command regex
        matching_processes = []
        for line in result.stdout.splitlines():
            if re.search(command_regex, line):
                parts = line.split(None, 10)
                if len(parts) >= 2:
                    try:
                        process_id = int(parts[1])
                        process_string = line
                        matching_processes.append({"processId": process_id, "processString": process_string})
                    except ValueError:
                        continue
        
        return jsonify(matching_processes), 200
    
    except Exception as e:
        return jsonify({"code": 500, "message": f"Internal Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)