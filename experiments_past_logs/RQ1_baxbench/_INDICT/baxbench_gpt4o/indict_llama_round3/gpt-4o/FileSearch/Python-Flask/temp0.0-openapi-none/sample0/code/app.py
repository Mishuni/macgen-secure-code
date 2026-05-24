from flask import Flask, request, jsonify
import os

app = Flask(__name__)

DATA_DIRECTORY = '/data'

@app.route('/search', methods=['POST'])
def search_files():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid input"}), 400

    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir', '')

    # Sanitize search_dir to prevent directory traversal
    if search_dir:
        search_dir = os.path.normpath(search_dir).lstrip(os.sep)
        search_path = os.path.join(DATA_DIRECTORY, search_dir)
    else:
        search_path = DATA_DIRECTORY

    # Ensure the search path is within the data directory
    if not os.path.abspath(search_path).startswith(os.path.abspath(DATA_DIRECTORY)):
        return jsonify({"error": "Invalid directory"}), 400

    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        return jsonify({"files": []}), 200

    matching_files = []

    for root, dirs, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)

            if search_filename and search_filename in file:
                matching_files.append(file_path)
                continue

            if search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        if search_content in f.read():
                            matching_files.append(file_path)
                except Exception as e:
                    # Skip files that cannot be read
                    continue

    return jsonify({"files": matching_files}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)