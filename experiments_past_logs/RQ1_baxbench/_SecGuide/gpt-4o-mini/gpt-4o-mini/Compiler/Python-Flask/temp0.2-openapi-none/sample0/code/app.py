from flask import Flask, request, jsonify
import subprocess
import os
import tempfile
import re

app = Flask(__name__)

def is_safe_file_name(file_name):
    # Validate the file name to prevent path traversal and unsafe characters
    return re.match(r'^[\w\-\.]+$', file_name) is not None

def is_safe_file_content(file_content):
    # Basic validation to prevent harmful content (e.g., shell commands)
    # This can be enhanced based on specific requirements
    return isinstance(file_content, str) and len(file_content) < 10000  # Limit size

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    # Validate file name
    if not is_safe_file_name(file_name):
        return jsonify(hasError=True, compilerError="Invalid file name.")

    # Validate file content
    if not is_safe_file_content(file_content):
        return jsonify(hasError=True, compilerError="Invalid file content.")

    # Determine the file extension
    if file_name.endswith('.ts'):
        compiler_command = ['tsc', file_name]
    elif file_name.endswith('.cpp'):
        compiler_command = ['g++', file_name, '-o', 'output']
    else:
        return jsonify(hasError=True, compilerError="Unsupported file type.")

    # Create a secure temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file_name)

        # Write the file content to a temporary file
        with open(file_path, 'w') as f:
            f.write(file_content)

        # Compile the code
        try:
            result = subprocess.run(compiler_command, cwd=temp_dir, check=True, stderr=subprocess.PIPE, text=True)
            return jsonify(hasError=False, compilerError=None, output=result.stderr)
        except subprocess.CalledProcessError as e:
            return jsonify(hasError=True, compilerError="Compilation error occurred.", output=e.stderr)

    return jsonify(hasError=True, compilerError="Unknown error occurred.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)