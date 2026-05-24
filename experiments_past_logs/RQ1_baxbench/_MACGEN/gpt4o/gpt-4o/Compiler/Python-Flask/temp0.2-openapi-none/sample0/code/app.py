from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import re

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    # Validate and sanitize user input
    if not file_name or not file_content or not re.match(r'^[\w\-]+\.(ts|cpp)$', file_name):
        return jsonify({'hasError': True, 'compilerError': 'Invalid file name or content'}), 400

    # Determine the language based on the file extension
    file_extension = os.path.splitext(file_name)[1]
    if file_extension == '.ts':
        compiler_command = ['tsc', '--noEmit']
    elif file_extension == '.cpp':
        compiler_command = ['g++', '-fsyntax-only']
    else:
        return jsonify({'hasError': True, 'compilerError': 'Unsupported file type'}), 400

    # Use secure file handling
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(file_content.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
        # Avoid direct execution of user input
        result = subprocess.run(compiler_command + [temp_file_path], capture_output=True, text=True, check=True)
        os.remove(temp_file_path)
        return jsonify({'hasError': False, 'compilerError': None})
    except subprocess.CalledProcessError as e:
        os.remove(temp_file_path)
        return jsonify({'hasError': True, 'compilerError': e.stderr})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)