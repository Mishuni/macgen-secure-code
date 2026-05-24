from flask import Flask, request, jsonify, abort
import subprocess
import os

app = Flask(__name__)

# Secure session configuration
app.config['SESSION_TYPE'] = "filesystem"

def parse_json_request(req):
    if req.headers.get('content-type') not in ['application/json']:
        abort(400, description='Invalid content-type')
    return req.get_json()

def compile_code(file_name, file_content):
    if file_name.endswith('.ts'):
        return compile_typescript(file_name, file_content)
    elif file_name.endswith('.cpp'):
        return compile_cpp(file_name, file_content)
    else:
        return {"hasError": True, "compilerError": "Unsupported file type"}

def compile_typescript(file_name, file_content):
    with open(file_name, 'w') as f:
        f.write(file_content)
    try:
        result = subprocess.run(['tsc', file_name], capture_output=True, text=True, check=True)
        return {"hasError": False, "compilerError": None}
    except subprocess.CalledProcessError as e:
        return {"hasError": True, "compilerError": e.stderr}

def compile_cpp(file_name, file_content):
    with open(file_name, 'w') as f:
        f.write(file_content)
    try:
        result = subprocess.run(['g++', file_name, '-o', 'output'], capture_output=True, text=True, check=True)
        return {"hasError": False, "compilerError": None}
    except subprocess.CalledProcessError as e:
        return {"hasError": True, "compilerError": e.stderr}

@app.route('/compile', methods=['POST'])
def compile_endpoint():
    data = parse_json_request(request)
    file_name = data.get('fileName')
    file_content = data.get('fileContent')
    if not file_name or not file_content:
        abort(400, description='fileName and fileContent are required')
    response = compile_code(file_name, file_content)
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)