from flask import Flask, request, jsonify
import os

app = Flask(__name__)

DATA_DIR = '/data'

def sanitize_path(search_dir):
    # Normalize the path and ensure it starts with DATA_DIR
    normalized_path = os.path.normpath(os.path.join(DATA_DIR, search_dir))
    if not normalized_path.startswith(DATA_DIR):
        raise ValueError("Invalid directory path")
    return normalized_path

def search_files(search_content, search_filename, search_dir):
    matched_files = []
    search_dir = sanitize_path(search_dir) if search_dir else DATA_DIR

    for root, _, files in os.walk(search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if search_filename and search_filename not in file:
                continue
            
            if search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        if search_content in f.read():
                            matched_files.append(file_path)
                except Exception as e:
                    # Handle file read errors (e.g., binary files)
                    continue
            else:
                matched_files.append(file_path)

    return matched_files

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir')

    if not isinstance(search_content, (str, type(None))) or not isinstance(search_filename, (str, type(None))) or not isinstance(search_dir, (str, type(None))):
        return jsonify({"error": "Invalid input"}), 400

    try:
        files = search_files(search_content, search_filename, search_dir)
        return jsonify({"files": files}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)