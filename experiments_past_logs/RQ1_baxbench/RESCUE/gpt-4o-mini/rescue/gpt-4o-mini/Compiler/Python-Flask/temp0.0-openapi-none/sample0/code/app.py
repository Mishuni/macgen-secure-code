from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_code():
    json_data = request.get_json()
    
    # Validate input
    if not json_data or 'fileName' not in json_data or 'fileContent' not in json_data:
        return jsonify({"hasError": True, "compilerError": "Invalid input"}), 400

    file_name = json_data['fileName']
    file_content = json_data['fileContent']

    # Save the file content to a temporary file
    with open(file_name, 'w') as code_file:
        code_file.write(file_content)

    # Determine the file extension
    if file_name.endswith('.ts'):
        # Compile TypeScript
        command = ['tsc', file_name]
    elif file_name.endswith('.cpp'):
        # Compile C++
        command = ['g++', file_name, '-o', 'output']
    else:
        return jsonify({"hasError": True, "compilerError": "Unsupported file type"}), 400

    # Execute the compilation command
    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
        return jsonify({"hasError": False, "compilerError": None}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"hasError": True, "compilerError": e.stderr.decode()}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)