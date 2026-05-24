from flask import Flask, request, jsonify, send_file, abort
import os
import uuid

app = Flask(__name__)

# Directory to store uploaded images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# General Security Guidelines
def secure_filename(filename):
    # Sanitize the filename to prevent directory traversal
    return os.path.basename(filename)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Sanitize and validate the filename
    filename = secure_filename(file.filename)
    
    # Generate a unique ID for the image
    image_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_FOLDER, image_id)

    # Save the file
    file.save(file_path)

    return jsonify({'id': image_id}), 200

@app.route('/images/<imageId>', methods=['GET'])
def share_image(imageId):
    file_path = os.path.join(UPLOAD_FOLDER, imageId)

    if not os.path.isfile(file_path):
        return jsonify({'error': 'Image not found'}), 404

    return send_file(file_path, mimetype='image/*', as_attachment=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)