from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search_files():
    data = request.get_json()

    search_content = data.get('search_content')
    search_filename = data.get('search_filename')
    search_dir = data.get('search_dir', '')

    # Validate input types
    if not isinstance(search_content, (str, type(None))) or not isinstance(search_filename, (str, type(None))) or not isinstance(search_dir, (str, type(None))):
        return jsonify({"error": "Invalid input"}), 400

    # Sanitize and validate search_dir
    normalized_dir = os.path.normpath(search_dir)
    if any(part in ('..', '') for part in normalized_dir.split(os.sep)):
        return jsonify({"error": "Invalid directory"}), 400

    base_path = '/data'
    search_path = os.path.join(base_path, normalized_dir.lstrip('/'))

    # Ensure the search path is within the base directory
    if not os.path.abspath(search_path).startswith(os.path.abspath(base_path)):
        return jsonify({"error": "Invalid directory"}), 400

    matching_files = []

    for root, dirs, files in os.walk(search_path):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Check filename match
            if search_filename and not filename.startswith(search_filename):
                continue

            # Check content match
            if search_content:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if search_content in content:
                            matching_files.append(file_path)
                except Exception:
                    continue
            else:
                matching_files.append(file_path)

    return jsonify({"files": matching_files})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)