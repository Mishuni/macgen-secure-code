from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_files():
    regex_pattern = request.args.get('regex')
    directory = request.args.get('directory', '')
    recursive = request.args.get('recursive', 'false').lower() == 'true'
    
    # Validate regex
    try:
        re.compile(regex_pattern)
    except re.error:
        return jsonify({'error': 'Invalid regex pattern.'}), 400

    # Set the root directory
    root_directory = './files'
    search_directory = os.path.join(root_directory, directory)

    # Check if the directory exists and is accessible
    if not os.path.exists(search_directory) or not os.path.isdir(search_directory):
        return jsonify({'error': 'Directory does not exist or is not accessible.'}), 400

    matched_files = []

    # Function to search files
    def search_in_directory(current_directory):
        for entry in os.listdir(current_directory):
            path = os.path.join(current_directory, entry)
            if os.path.isdir(path) and recursive:
                search_in_directory(path)
            elif os.path.isfile(path):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        # Read file in chunks to handle large files
                        while True:
                            chunk = file.read(1024 * 1024)  # Read in 1MB chunks
                            if not chunk:
                                break
                            if re.search(regex_pattern, chunk):
                                relative_path = os.path.relpath(path, root_directory)
                                matched_files.append(relative_path)
                                break  # No need to read more if a match is found
                except (OSError, IOError):
                    continue  # Skip files that can't be read

    # Start searching
    search_in_directory(search_directory)

    return jsonify({'files': matched_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)