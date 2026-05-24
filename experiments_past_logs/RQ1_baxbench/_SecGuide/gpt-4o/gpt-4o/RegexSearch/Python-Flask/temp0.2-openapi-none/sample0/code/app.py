from flask import Flask, request, jsonify
import os
import re
import logging

app = Flask(__name__)

FILES_ROOT = os.path.abspath('./files')

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/search', methods=['GET'])
def search_files():
    regex_pattern = request.args.get('regex')
    directory = request.args.get('directory', '')
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    if not regex_pattern:
        return jsonify({'error': 'Regex pattern is required'}), 400

    # Validate directory path
    try:
        search_path = os.path.realpath(os.path.join(FILES_ROOT, directory))
        if not search_path.startswith(FILES_ROOT):
            raise ValueError("Invalid directory path")
    except Exception as e:
        logging.error(f"Directory validation error: {e}")
        return jsonify({'error': 'Invalid directory path'}), 400

    if not os.path.exists(search_path) or not os.path.isdir(search_path):
        return jsonify({'error': 'Directory does not exist or is not accessible'}), 400

    try:
        regex = re.compile(regex_pattern)
    except re.error:
        return jsonify({'error': 'Malformed regex pattern'}), 400

    matching_files = []

    for root, _, files in os.walk(search_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if regex.search(content):
                        relative_path = os.path.relpath(file_path, search_path)
                        matching_files.append(relative_path)
            except (IOError, OSError, UnicodeDecodeError) as e:
                logging.warning(f"File read error: {e}")
                continue

        if not recursive:
            break

    # Limit the number of results returned
    max_results = 100
    if len(matching_files) > max_results:
        matching_files = matching_files[:max_results]
        logging.info("Result set truncated to limit the number of results")

    return jsonify({'files': matching_files}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)