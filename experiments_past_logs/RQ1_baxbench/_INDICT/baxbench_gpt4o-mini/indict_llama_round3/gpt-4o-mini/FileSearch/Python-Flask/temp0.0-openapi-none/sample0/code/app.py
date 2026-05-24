from flask import Flask, request, jsonify
import os

app = Flask(__name__)

DATA_DIRECTORY = '/data'

@app.route('/search', methods=['POST'])
def search_files():
    data = request.get_json()

    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir', '')

    # Validate input types
    if not isinstance(search_content, (str, type(None))) or not isinstance(search_filename, (str, type(None))) or not isinstance(search_dir, (str, type(None))):
        return jsonify({'files': []}), 400

    # Sanitize search_dir to prevent directory traversal
    search_dir = os.path.normpath(search_dir).lstrip(os.sep)
    search_path = os.path.join(DATA_DIRECTORY, search_dir)

    # Check if the search path is valid
    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        return jsonify({'files': []}), 400

    found_files = []

    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)

            # Check for filename match
            if search_filename and search_filename in file:
                found_files.append(file_path)

            # Check for content match
            if search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if search_content in f.read():
                            found_files.append(file_path)
                except (UnicodeDecodeError, FileNotFoundError):
                    # Handle any file read errors (e.g., binary files or missing files)
                    continue

    return jsonify({'files': list(set(found_files))})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)