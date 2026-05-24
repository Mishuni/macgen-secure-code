from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_files():
    regex_pattern = request.args.get('regex')
    directory = request.args.get('directory', './files')
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    # Validate regex pattern
    if not regex_pattern:
        return jsonify({'error': 'Regex pattern is required.'}), 400
    if len(regex_pattern) > 100:  # Limit regex length
        return jsonify({'error': 'Regex pattern is too long.'}), 400

    try:
        compiled_regex = re.compile(regex_pattern)
    except re.error:
        return jsonify({'error': 'Invalid regex pattern.'}), 400

    matching_files = []
    base_directory = os.path.abspath('./files')

    # Validate directory
    target_directory = os.path.abspath(directory)
    if not os.path.commonpath([base_directory, target_directory]) == base_directory:
        return jsonify({'error': 'Invalid directory.'}), 400

    for root, dirs, files in os.walk(target_directory):
        for file in files:
            file_path = os.path.join(root, file)
            if not file_path.startswith(base_directory):
                continue  # Skip files outside the allowed directory
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if compiled_regex.search(content):
                        relative_path = os.path.relpath(file_path, base_directory)
                        matching_files.append(relative_path)
            except Exception:
                continue  # Skip files that can't be read

        if not recursive:
            break  # Stop searching deeper if not recursive

    return jsonify({'files': matching_files}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)