from flask import Flask, request, jsonify
import os
import re

app = Flask(__name__)

@app.route('/search', methods=['GET'])
def search_files():
    try:
        regex_pattern = request.args.get('regex')
        directory = request.args.get('directory', '')
        recursive = request.args.get('recursive', 'false').lower() == 'true'

        if not regex_pattern:
            return jsonify({'error': 'Regex pattern is required'}), 400

        if len(regex_pattern) > 100:
            return jsonify({'error': 'Regex pattern too long'}), 400

        try:
            regex = re.compile(regex_pattern)
        except re.error:
            return jsonify({'error': 'Invalid regex pattern'}), 400

        root_dir = os.path.join('.', 'files', directory)
        if not os.path.exists(root_dir) or not os.path.isdir(root_dir):
            return jsonify({'error': 'Directory does not exist or is not accessible'}), 400

        if not os.path.commonpath([os.path.realpath(root_dir), os.path.realpath('./files')]) == os.path.realpath('./files'):
            return jsonify({'error': 'Invalid directory path'}), 400

        matching_files = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if regex.search(content):
                            relative_path = os.path.relpath(file_path, root_dir)
                            matching_files.append(relative_path)
                except (IOError, OSError):
                    continue

            if not recursive:
                break

        return jsonify({'files': matching_files}), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)