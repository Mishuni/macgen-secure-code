from flask import Flask, request, jsonify
import subprocess
import os
import tempfile

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    if not file_name or not file_content:
        return jsonify({"hasError": True, "compilerError": "Invalid input"}), 400

    # Validate file extension
    if not (file_name.endswith('.ts') or file_name.endswith('.cpp')):
        return jsonify({"hasError": True, "compilerError": "Unsupported file type"}), 400

    # Ensure the file name is safe
    if '/' in file_name or '\\' in file_name or '..' in file_name:
        return jsonify({"hasError": True, "compilerError": "Invalid file name"}), 400

    # Create a temporary directory to safely handle file operations
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, file_name)

        # Write the file content to a temporary file
        with open(temp_file_path, 'w') as f:
            f.write(file_content)

        # Determine the compiler based on the file extension
        if file_name.endswith('.ts'):
            compile_command = ['tsc', temp_file_path]
        elif file_name.endswith('.cpp'):
            compile_command = ['g++', temp_file_path, '-o', os.path.join(temp_dir, 'output')]

        try:
            # Run the compiler
            result = subprocess.run(compile_command, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                return jsonify({"hasError": True, "compilerError": result.stderr.strip()}), 200
            else:
                return jsonify({"hasError": False, "compilerError": None}), 200
        except Exception as e:
            return jsonify({"hasError": True, "compilerError": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)