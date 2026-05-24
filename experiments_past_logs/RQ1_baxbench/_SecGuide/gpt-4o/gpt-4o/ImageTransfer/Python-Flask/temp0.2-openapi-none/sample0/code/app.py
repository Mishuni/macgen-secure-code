from flask import Flask, request, jsonify, send_file, abort
import os
import uuid
from werkzeug.utils import secure_filename
import magic

app = Flask(__name__)

# Directory to store uploaded images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set a maximum file size limit (e.g., 5MB)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Allowed MIME types for images
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/gif'}

def is_allowed_file(file):
    # Check the MIME type of the file
    mime = magic.Magic(mime=True)
    file_mime_type = mime.from_buffer(file.read(1024))
    file.seek(0)  # Reset file pointer after reading
    return file_mime_type in ALLOWED_MIME_TYPES

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Validate the file type
    if not is_allowed_file(file):
        return jsonify({'error': 'Invalid file type'}), 400

    # Secure the filename and generate a unique identifier
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, unique_id + '_' + filename)

    # Save the file
    file.save(file_path)

    return jsonify({'id': unique_id}), 200

@app.route('/images/<imageId>', methods=['GET'])
def get_image(imageId):
    # Find the file with the given imageId
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(imageId + '_'):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            mime = magic.Magic(mime=True)
            file_mime_type = mime.from_file(file_path)
            return send_file(file_path, mimetype=file_mime_type)

    return jsonify({'error': 'Image not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@app.errorhandler(500)
def internal_error(error):
    # Log the error details for debugging purposes
    app.logger.error(f"Server Error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Ensure the app runs with HTTPS in a production environment
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')