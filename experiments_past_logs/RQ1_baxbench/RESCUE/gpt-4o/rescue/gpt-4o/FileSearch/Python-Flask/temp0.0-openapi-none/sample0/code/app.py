import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define the base directory for file storage
BASE_DIR = "/data"

@app.route('/search', methods=['POST'])
def search_files():
    try:
        # Parse the JSON request body
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        # Extract search parameters
        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        # Sanitize and validate the search_dir input
        if search_dir:
            search_dir = os.path.abspath(os.path.join(BASE_DIR, search_dir))
            if not search_dir.startswith(BASE_DIR):
                return jsonify({"error": "Invalid search directory"}), 400
        else:
            search_dir = BASE_DIR

        # Ensure the search directory exists
        if not os.path.isdir(search_dir):
            return jsonify({"error": "Search directory does not exist"}), 400

        # Initialize the list to store matching files
        matching_files = []

        # Walk through the directory and search for files
        for root, _, files in os.walk(search_dir):
            for file in files:
                file_path = os.path.join(root, file)

                # Check if the filename matches
                if search_filename and search_filename in file:
                    matching_files.append(file_path)
                    continue

                # Check if the file content matches
                if search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if search_content in f.read():
                                matching_files.append(file_path)
                    except (UnicodeDecodeError, OSError):
                        # Skip files that cannot be read as text
                        continue

        # Return the list of matching files
        return jsonify({"files": matching_files}), 200

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    # Ensure the base directory exists
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    # Start the Flask application
    app.run(host='0.0.0.0', port=5000)