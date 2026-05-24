from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_files():
    regex_pattern = request.args.get('regex')
    directory = request.args.get('directory', '')
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    # Validate regex pattern
    try:
        re.compile(regex_pattern)
    except re.error:
        return jsonify({"error": "Invalid regex pattern."}), 400

    # Define the root directory
    root_directory = './files'
    search_directory = os.path.join(root_directory, directory)

    # Check if the directory exists
    if not os.path.exists(search_directory) or not os.path.isdir(search_directory):
        return jsonify({"error": "Directory does not exist or is not accessible."}), 400

    matched_files = []

    # Function to search files
    def search_in_directory(path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path) and recursive:
                search_in_directory(full_path)
            elif os.path.isfile(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if re.search(regex_pattern, content):
                        relative_path = os.path.relpath(full_path, root_directory)
                        matched_files.append(relative_path)

    # Start searching
    search_in_directory(search_directory)

    return jsonify({"files": matched_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)