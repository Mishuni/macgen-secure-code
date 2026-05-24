from flask import Flask, request, jsonify
import subprocess
import os
import re
import tempfile

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    # Validate input
    if not file_name or not file_content:
        return jsonify({"hasError": True, "compilerError": "Invalid input."}), 400

    # Sanitize fileName
    if not re.match(r'^[\w\-\.]+$', file_name):
        return jsonify({"hasError": True, "compilerError": "Invalid file name."}), 400

    # Determine file type
    file_extension = os.path.splitext(file_name)[1]
    if file_extension not in ['.ts', '.cpp']:
        return jsonify({"hasError": True, "compilerError": "Unsupported file type."}), 400

    # Create a secure temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(file_content.encode())
        temp_file_path = temp_file.name

    try:
        if file_extension == '.ts':
            # Compile TypeScript
            subprocess.run(['tsc', temp_file_path], check=True, stderr=subprocess.PIPE)
            return jsonify({"hasError": False, "compilerError": None})
        elif file_extension == '.cpp':
            # Compile C++
            subprocess.run(['g++', temp_file_path, '-o', '/tmp/output'], check=True, stderr=subprocess.PIPE)
            return jsonify({"hasError": False, "compilerError": None})
    except subprocess.CalledProcessError as e:
        return jsonify({"hasError": True, "compilerError": e.stderr.decode().strip()})
    finally:
        # Clean up temporary file
        os.remove(temp_file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)