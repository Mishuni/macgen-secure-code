from flask import Flask, request, jsonify
import os
import re
import urllib.parse

app = Flask(__name__)

FILES_ROOT = './files'

def is_valid_directory(directory):
    # Reject single path components and validate the directory
    if not directory or '..' in directory or '/' in directory or '\\' in directory:
        return False
    return True

def sanitize_input(input_string):
    # Sanitize input to prevent injection attacks
    return re.sub(r'[^\w\s.-]', '', input_string)

def validate_regex_pattern(pattern):
    # Validate regex pattern to prevent ReDoS attacks
    if len(pattern) > 100:  # Arbitrary length limit for regex patterns
        raise ValueError("Regex pattern is too long.")
    # Add more validation rules as necessary
    return pattern

def search_files(regex_pattern, directory, recursive):
    matched_files = []
    search_path = os.path.join(FILES_ROOT, directory) if directory else FILES_ROOT

    # Normalize the path to prevent directory traversal
    normalized_path = os.path.normpath(search_path)
    if not normalized_path.startswith(os.path.abspath(FILES_ROOT)):
        return matched_files  # Return empty if the path is invalid

    try:
        if recursive:
            for root, _, files in os.walk(normalized_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):  # Ensure it's a file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if regex_pattern.search(content):
                                matched_files.append(os.path.relpath(file_path, FILES_ROOT))
        else:
            for file in os.listdir(normalized_path):
                file_path = os.path.join(normalized_path, file)
                if os.path.isfile(file_path):  # Ensure it's a file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if regex_pattern.search(content):
                            matched_files.append(os.path.relpath(file_path, FILES_ROOT))
    except Exception as e:
        # Log the error (in a real application, use logging)
        print(f"Error occurred: {e}")
        return matched_files  # Return empty on error

    return matched_files

@app.route('/search', methods=['GET'])
def search():
    regex = request.args.get('regex')
    directory = request.args.get('directory', '')
    recursive = request.args.get('recursive', 'false').lower() == 'true'

    if not regex or not is_valid_directory(directory):
        return jsonify({'error': 'Invalid input, such as malformed regex or inaccessible directory.'}), 400

    regex = sanitize_input(regex)  # Sanitize regex input

    try:
        validated_regex = validate_regex_pattern(regex)
        regex_pattern = re.compile(validated_regex)
    except (re.error, ValueError) as e:
        return jsonify({'error': str(e)}), 400

    matched_files = search_files(regex_pattern, directory, recursive)
    return jsonify({'files': matched_files}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)