import os
import re
from flask import Flask, request, jsonify

app = Flask(__name__)

# Root directory for file storage
FILES_ROOT = "./files"

@app.route('/search', methods=['GET'])
def search_files():
    try:
        # Get query parameters
        regex = request.args.get('regex')
        directory = request.args.get('directory', '')
        recursive = request.args.get('recursive', 'false').lower() == 'true'

        # Validate regex parameter
        if not regex:
            return jsonify({"error": "The 'regex' query parameter is required."}), 400
        try:
            compiled_regex = re.compile(regex)
        except re.error:
            return jsonify({"error": "Invalid regex pattern."}), 400

        # Construct the search directory path
        search_directory = os.path.join(FILES_ROOT, directory)
        if not os.path.exists(search_directory) or not os.path.isdir(search_directory):
            return jsonify({"error": "The specified directory does not exist or is not accessible."}), 400

        # Search for files matching the regex
        matching_files = []
        for root, dirs, files in os.walk(search_directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if compiled_regex.search(content):
                            # Add the file path relative to the search directory
                            relative_path = os.path.relpath(file_path, search_directory)
                            matching_files.append(relative_path)
                except (OSError, UnicodeDecodeError):
                    # Skip files that cannot be read
                    continue
            if not recursive:
                break

        # Return the matching files
        return jsonify({"files": matching_files}), 200

    except Exception as e:
        # Handle unexpected server errors
        return jsonify({"error": "Internal server error."}), 500

if __name__ == '__main__':
    # Ensure the files root directory exists
    if not os.path.exists(FILES_ROOT):
        os.makedirs(FILES_ROOT)
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000)