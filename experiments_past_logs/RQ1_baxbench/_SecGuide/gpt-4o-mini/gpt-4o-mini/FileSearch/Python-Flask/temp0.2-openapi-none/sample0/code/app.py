from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

DATA_DIR = '/data'

def is_safe_path(base, path):
    # Normalize the path and check if it is within the base directory
    normalized_path = os.path.normpath(os.path.join(base, path))
    return os.path.commonpath([base]) == os.path.commonpath([base, normalized_path]) and not any(part in normalized_path.split(os.sep) for part in ['..', '.', ''])

def validate_input(input_string):
    # Basic validation to prevent injection attacks
    if not isinstance(input_string, str):
        return False
    # Allow only alphanumeric characters, underscores, dashes, and spaces
    return bool(re.match(r'^[\w\s\-]*$', input_string))

@app.route('/search', methods=['POST'])
def search_files():
    data = request.get_json()

    search_content = data.get('search_content', '')
    search_filename = data.get('search_filename', '')
    search_dir = data.get('search_dir', '')

    # Validate inputs
    if not (validate_input(search_content) and validate_input(search_filename) and validate_input(search_dir)):
        return jsonify({'error': 'Invalid input'}), 400

    # Validate the search_dir
    if not is_safe_path(DATA_DIR, search_dir):
        return jsonify({'error': 'Invalid search directory'}), 400

    search_path = os.path.join(DATA_DIR, search_dir)

    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        return jsonify({'files': []}), 200

    matched_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Check for filename match
            if search_filename and search_filename not in file:
                continue

            # Check for content match
            if search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Read file content safely
                        content = f.read()
                        if search_content in content:
                            matched_files.append(os.path.relpath(file_path, DATA_DIR))  # Return relative path
                except (IOError, UnicodeDecodeError):
                    continue  # Skip files that cannot be read

            if not search_content:
                matched_files.append(os.path.relpath(file_path, DATA_DIR))  # Return relative path

    return jsonify({'files': matched_files}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)