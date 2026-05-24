from flask import Flask, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
import logging
import mimetypes

app = Flask(__name__)

# Directory where songs are stored
SONG_DIRECTORY = '/var/songs'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp3', 'wav'}

# Configure logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_path(base_path, path, follow_symlinks=True):
    # Resolve symbolic links
    if follow_symlinks:
        return os.path.realpath(path).startswith(base_path)
    return os.path.abspath(path).startswith(base_path)

@app.route('/download', methods=['POST'])
def download_song():
    # Validate request content type
    if request.content_type != 'application/json':
        return jsonify({'error': 'Invalid content type'}), 400

    # Validate request data
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    filename = data['filename']

    # Secure the filename
    secure_name = secure_filename(filename)

    # Validate file extension
    if not allowed_file(secure_name):
        return jsonify({'error': 'Invalid file type'}), 400

    # Construct the full file path
    file_path = os.path.join(SONG_DIRECTORY, secure_name)

    # Ensure the file path is safe
    if not is_safe_path(SONG_DIRECTORY, file_path):
        return jsonify({'error': 'Invalid file path'}), 400

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File does not exist'}), 404

    # Log the file access attempt
    logging.info(f"File requested: {secure_name} from IP: {request.remote_addr}")

    # Determine the correct MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    # Stream the file
    return send_from_directory(SONG_DIRECTORY, secure_name, mimetype=mime_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)