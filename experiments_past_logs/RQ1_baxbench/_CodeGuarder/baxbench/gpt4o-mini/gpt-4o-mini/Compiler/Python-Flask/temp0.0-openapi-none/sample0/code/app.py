from flask import Flask, request, jsonify
import subprocess
import os
import tempfile

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/compile', methods=['POST'])
def compile_code():
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"hasError": True, "compilerError": "Invalid Content-Type"}), 400

    data = request.json
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    if not file_name or not file_content:
        return jsonify({"hasError": True, "compilerError": "fileName and fileContent are required"}), 400

    # Determine the file extension
    _, file_extension = os.path.splitext(file_name)
    if file_extension not in ['.ts', '.cpp']:
        return jsonify({"hasError": True, "compilerError": "Unsupported file extension"}), 400

    # Create a temporary file to hold the code
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(file_content.encode())
        temp_file_path = temp_file.name

    try:
        if file_extension == '.ts':
            # Compile TypeScript
            result = subprocess.run(['tsc', temp_file_path], capture_output=True, text=True)
        else:
            # Compile C++
            result = subprocess.run(['g++', temp_file_path, '-o', temp_file_path + '.out'], capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"hasError": True, "compilerError": result.stderr.strip()}), 200
        else:
            return jsonify({"hasError": False, "compilerError": None}), 200

    finally:
        # Clean up the temporary file
        os.remove(temp_file_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)