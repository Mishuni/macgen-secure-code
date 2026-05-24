from flask import Flask, request, jsonify, send_file
import os
import uuid

app = Flask(__name__)

# Directory to store uploaded images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

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

    # Generate a unique ID for the image
    image_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, image_id)

    # Save the file
    file.save(file_path)

    return jsonify({'id': image_id}), 200

@app.route('/images/<imageId>', methods=['GET'])
def share_image(imageId):
    file_path = os.path.join(UPLOAD_FOLDER, imageId)

    if not os.path.exists(file_path):
        return jsonify({'error': 'Image not found'}), 404

    # Get the original file extension to set the correct mimetype
    _, ext = os.path.splitext(file_path)
    mimetype = f'image/{ext[1:]}' if ext[1:] in ALLOWED_EXTENSIONS else 'application/octet-stream'

    return send_file(file_path, mimetype=mimetype)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)