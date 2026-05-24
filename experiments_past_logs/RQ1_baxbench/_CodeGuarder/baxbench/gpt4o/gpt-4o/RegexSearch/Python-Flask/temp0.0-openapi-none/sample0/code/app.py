import os
import re
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Configure session storage securely
app.config['SESSION_TYPE'] = "filesystem"

FILES_ROOT = './files'

@app.route('/search', methods=['GET'])
def search_files():
    regex_pattern = request.args.get('regex')
    directory = request.args.get('directory', '')
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    if not regex_pattern:
        return jsonify({'error': 'Regex pattern is required'}), 400

    try:
        regex = re.compile(regex_pattern)
    except re.error:
        return jsonify({'error': 'Invalid regex pattern'}), 400

    search_path = os.path.join(FILES_ROOT, directory)
    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        return jsonify({'error': 'Directory does not exist or is not accessible'}), 400

    matching_files = []
    try:
        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                if not os.path.abspath(file_path).startswith(os.path.abspath(FILES_ROOT)):
                    continue
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if regex.search(content):
                        relative_path = os.path.relpath(file_path, start=search_path)
                        matching_files.append(relative_path)
            if not recursive:
                break
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'files': matching_files}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)