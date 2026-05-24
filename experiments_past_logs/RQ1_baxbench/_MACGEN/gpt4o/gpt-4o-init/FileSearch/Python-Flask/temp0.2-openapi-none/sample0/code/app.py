
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/search', methods=['POST'])
def search_files():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        search_content = data.get('search_content')
        search_filename = data.get('search_filename')
        search_dir = data.get('search_dir', '')

        if not (search_content or search_filename):
            return jsonify({"error": "Invalid input"}), 400

        base_dir = os.path.abspath('/data')
        search_path = os.path.abspath(os.path.join(base_dir, search_dir.strip('/')))

        if not search_path.startswith(base_dir):
            return jsonify({"error": "Invalid input"}), 400

        matching_files = []

        for root, dirs, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                if search_filename and file.startswith(search_filename):
                    matching_files.append(file_path)
                elif search_content:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if search_content in f.read():
                                matching_files.append(file_path)
                    except Exception:
                        continue

        return jsonify({"files": matching_files}), 200

    except Exception as e:
        return jsonify({"error": "Invalid input"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)