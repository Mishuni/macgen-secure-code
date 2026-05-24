import os
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Set the base directory for file searches
BASE_DIRECTORY = os.path.abspath('/data')

@app.route('/search', methods=['POST'])
def search_files():
    # Validate content-type
    if request.headers.get('content-type') != 'application/json':
        abort(400, description='Invalid content-type')

    # Parse and validate request data
    data = request.get_json()
    if not data:
        abort(400, description='Invalid JSON data')

    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir', '')

    if not isinstance(search_content, (str, type(None))) or not isinstance(search_filename, (str, type(None))) or not isinstance(search_dir, (str, type(None))):
        abort(400, description='Invalid input types')

    # Resolve and validate the search directory
    search_path = os.path.normpath(os.path.join(BASE_DIRECTORY, search_dir))
    if not search_path.startswith(BASE_DIRECTORY):
        abort(400, description='Invalid search directory')

    # Search for files
    matching_files = []
    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            if search_filename and search_filename in file:
                matching_files.append(file_path)
            elif search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if search_content in f.read():
                            matching_files.append(file_path)
                except (IOError, UnicodeDecodeError):
                    continue

    # Construct and return the response
    return jsonify({'files': matching_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)