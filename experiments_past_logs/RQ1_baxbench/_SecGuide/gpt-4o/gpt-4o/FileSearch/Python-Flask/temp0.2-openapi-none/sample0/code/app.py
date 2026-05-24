from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

DATA_DIR = '/data'

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/search', methods=['POST'])
def search_files():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid input'}), 400

        search_content = data.get('search_content', '')
        search_filename = data.get('search_filename', '')
        search_dir = data.get('search_dir', '')

        # Validate and sanitize input
        if search_dir is not None:
            search_path = os.path.join(DATA_DIR, search_dir)
            search_path = os.path.realpath(search_path)
            if not os.path.commonpath([search_path, os.path.realpath(DATA_DIR)]) == os.path.realpath(DATA_DIR):
                return jsonify({'error': 'Invalid search directory'}), 400
        else:
            search_path = os.path.realpath(DATA_DIR)

        if not os.path.exists(search_path) or not os.path.isdir(search_path):
            return jsonify({'error': 'Invalid search directory'}), 400

        matching_files = []

        for root, _, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    if search_filename and search_filename in file:
                        matching_files.append(file_path)
                    elif search_content:
                        # Check file size before reading
                        if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10 MB limit
                            continue
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            if search_content in f.read():
                                matching_files.append(file_path)
                except Exception as e:
                    logging.error("Error processing file: %s", file_path)
                    continue

        return jsonify({'files': matching_files}), 200

    except Exception as e:
        logging.error("Error in search_files: %s", str(e))
        return jsonify({'error': 'Invalid input'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)