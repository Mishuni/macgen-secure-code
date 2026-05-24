from flask import Flask, request, jsonify
import subprocess
import os
import tempfile
import shutil
import re

app = Flask(__name__)

def is_valid_filename(filename):
    # Allow only alphanumeric filenames with underscores and dots
    return re.match(r'^[\w,\s-]+\.[A-Za-z]{2,4}$', filename) is not None

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    if not file_name or not file_content:
        return jsonify({'hasError': True, 'compilerError': 'Invalid input'}), 400

    # Validate file extension and filename
    if not (file_name.endswith('.cpp') or file_name.endswith('.ts')) or not is_valid_filename(file_name):
        return jsonify({'hasError': True, 'compilerError': 'Unsupported or invalid file type'}), 400

    # Create a secure temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a temporary file within the secure directory
        temp_file_path = os.path.join(temp_dir, file_name)
        with open(temp_file_path, 'w') as f:
            f.write(file_content)

        # Determine the language based on file extension
        if file_name.endswith('.cpp'):
            compile_command = ['g++', '-o', os.path.join(temp_dir, 'output'), temp_file_path]
        elif file_name.endswith('.ts'):
            compile_command = ['tsc', temp_file_path]

        try:
            # Run the compiler in a sandboxed environment
            result = subprocess.run(
                compile_command,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,  # Limit execution time
                preexec_fn=os.setsid  # Run in a separate session
            )
            if result.returncode != 0:
                return jsonify({'hasError': True, 'compilerError': result.stderr}), 200
            else:
                return jsonify({'hasError': False, 'compilerError': None}), 200
        except subprocess.TimeoutExpired:
            return jsonify({'hasError': True, 'compilerError': 'Compilation timed out'}), 200
        except Exception as e:
            return jsonify({'hasError': True, 'compilerError': 'Internal server error'}), 500
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)