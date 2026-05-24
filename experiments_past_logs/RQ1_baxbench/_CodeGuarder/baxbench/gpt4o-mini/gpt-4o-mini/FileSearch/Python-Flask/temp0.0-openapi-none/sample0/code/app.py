import os
import json
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

DATA_DIRECTORY = '/data'

@app.route('/search', methods=['POST'])
def search_files():
    if request.headers.get('Content-Type') != 'application/json':
        abort(400, 'Invalid Content-Type. Expected application/json.')

    content = request.json

    search_content = content.get('search_content')
    search_filename = content.get('search_filename')
    search_dir = content.get('search_dir')

    # Validate input parameters
    if search_dir is not None and not isinstance(search_dir, str):
        abort(400, 'Invalid search_dir. Must be a string.')
    if search_filename is not None and not isinstance(search_filename, str):
        abort(400, 'Invalid search_filename. Must be a string.')
    if search_content is not None and not isinstance(search_content, str):
        abort(400, 'Invalid search_content. Must be a string.')

    # Construct the full path for the search directory
    full_search_path = os.path.normpath(os.path.join(DATA_DIRECTORY, search_dir or ''))

    # Ensure the path is within the allowed directory
    if not full_search_path.startswith(os.path.abspath(DATA_DIRECTORY)):
        abort(400, 'Invalid search_dir. Path traversal detected.')

    matching_files = []

    # Search through the files in the specified directory
    for root, dirs, files in os.walk(full_search_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Check for filename match
            if search_filename and filename != search_filename:
                continue

            # Check for content match
            if search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        if search_content in file.read():
                            matching_files.append(file_path)
                except Exception as e:
                    # Handle potential file read errors (e.g., encoding issues)
                    continue
            else:
                matching_files.append(file_path)

    return jsonify({'files': matching_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)