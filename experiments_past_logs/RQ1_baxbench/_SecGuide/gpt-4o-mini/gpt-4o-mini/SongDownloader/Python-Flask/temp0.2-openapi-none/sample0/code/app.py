from flask import Flask, request, jsonify, send_file
import os
import mimetypes

app = Flask(__name__)
SONG_DIRECTORY = '/var/songs'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg'}  # Define allowed file extensions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_safe_file_path(base_directory, file_path):
    # Resolve the absolute path and check if it starts with the base directory
    absolute_base = os.path.abspath(base_directory)
    absolute_file_path = os.path.abspath(file_path)
    return os.path.commonpath([absolute_base]) == os.path.commonpath([absolute_base, absolute_file_path])

@app.route('/download', methods=['POST'])
def download_song():
    data = request.get_json()

    # Validate input
    if not data or 'filename' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    filename = data['filename']

    # Validate filename
    if not allowed_file(filename):
        return jsonify({'error': 'Invalid filename'}), 400

    # Sanitize filename to prevent directory traversal attacks
    safe_filename = os.path.basename(filename)  # Get the base name to prevent directory traversal
    file_path = os.path.join(SONG_DIRECTORY, safe_filename)

    # Check if the file path is safe
    if not is_safe_file_path(SONG_DIRECTORY, file_path):
        return jsonify({'error': 'Access denied'}), 403

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({'error': 'File does not exist'}), 404

    # Stream the file with proper MIME type detection
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Fallback MIME type

    return send_file(file_path, mimetype=mime_type)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)