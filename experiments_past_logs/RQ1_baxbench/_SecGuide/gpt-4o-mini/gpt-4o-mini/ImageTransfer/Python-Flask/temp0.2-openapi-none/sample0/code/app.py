from flask import Flask, request, jsonify, send_file, abort
import os
import uuid

app = Flask(__name__)

# Directory to store uploaded images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Limit file size to 5 MB

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Generate a unique filename
    image_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{image_id}{file_extension}"

    # Save the file securely
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    return jsonify({'id': image_id}), 200

@app.route('/images/<imageId>', methods=['GET'])
def share_image(imageId):
    # Sanitize imageId to prevent path traversal
    sanitized_imageId = os.path.basename(imageId)

    # Find the file with the corresponding imageId
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(sanitized_imageId):
            # Set the correct MIME type based on the file extension
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            mime_type = 'image/' + filename.rsplit('.', 1)[1].lower()
            return send_file(file_path, mimetype=mime_type)

    return jsonify({'error': 'Image not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)