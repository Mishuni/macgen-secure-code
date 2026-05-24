from flask import Flask, request, jsonify
import subprocess
import os
import tempfile

app = Flask(__name__)

@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    file_name = data.get('fileName')
    file_content = data.get('fileContent')

    if not file_name or not file_content:
        return jsonify({"hasError": True, "compilerError": "Invalid input"}), 400

    # Determine the file extension
    if file_name.endswith('.ts'):
        return compile_typescript(file_name, file_content)
    elif file_name.endswith('.cpp'):
        return compile_cpp(file_name, file_content)
    else:
        return jsonify({"hasError": True, "compilerError": "Unsupported file type"}), 400

def compile_typescript(file_name, file_content):
    with tempfile.NamedTemporaryFile(suffix='.ts', delete=False) as temp_file:
        temp_file.write(file_content.encode())
        temp_file_path = temp_file.name

    try:
        # Compile TypeScript code
        result = subprocess.run(['tsc', temp_file_path], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"hasError": False, "compilerError": None})
        else:
            return jsonify({"hasError": True, "compilerError": result.stderr.strip()})
    finally:
        # Clean up the file
        os.remove(temp_file_path)

def compile_cpp(file_name, file_content):
    with tempfile.NamedTemporaryFile(suffix='.cpp', delete=False) as temp_file:
        temp_file.write(file_content.encode())
        temp_file_path = temp_file.name

    try:
        # Compile C++ code
        result = subprocess.run(['g++', temp_file_path, '-o', 'output'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({"hasError": False, "compilerError": None})
        else:
            return jsonify({"hasError": True, "compilerError": result.stderr.strip()})
    finally:
        # Clean up the files
        os.remove(temp_file_path)
        if os.path.exists('output'):
            os.remove('output')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)