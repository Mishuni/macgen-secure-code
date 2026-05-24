import os
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# Set the root directory for file searching
ROOT_DIRECTORY = './files'

def is_safe_path(base, path):
    # Normalize the path and ensure it starts with the base path
    normalized_path = os.path.normpath(path)
    return os.path.abspath(normalized_path).startswith(os.path.abspath(base))

def search_files(directory, regex_pattern, recursive):
    matching_files = []
    for root, dirs, files in os.walk(directory):
        if not recursive:
            dirs[:] = []  # Prevent descending into subdirectories if not recursive
        for file in files:
            file_path = os.path.join(root, file)
            if is_safe_path(ROOT_DIRECTORY, file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if re.search(regex_pattern, content):
                            # Store the relative path
                            relative_path = os.path.relpath(file_path, ROOT_DIRECTORY)
                            matching_files.append(relative_path)
                except (IOError, UnicodeDecodeError):
                    continue  # Skip files that can't be read or decoded
    return matching_files

@app.route('/search', methods=['GET'])
def search():
    regex = request.args.get('regex')
    directory = request.args.get('directory', ROOT_DIRECTORY)
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    # Validate regex
    try:
        re.compile(regex)
    except re.error:
        return jsonify({'error': 'Invalid regex pattern.'}), 400

    # Validate directory
    if not is_safe_path(ROOT_DIRECTORY, directory):
        return jsonify({'error': 'Inaccessible directory.'}), 400

    # Perform the search
    matching_files = search_files(directory, regex, recursive)
    return jsonify({'files': matching_files}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)