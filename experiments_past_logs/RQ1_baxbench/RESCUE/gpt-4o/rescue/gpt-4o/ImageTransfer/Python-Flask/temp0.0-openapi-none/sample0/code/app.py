from flask import Flask, request, jsonify, send_file, abort
import os
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_image():
    """Endpoint to upload an image and return a shareable link."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    if file and allowed_file(file.filename):
        # Secure the filename
        filename = secure_filename(file.filename)
        # Generate a unique ID for the file
        unique_id = str(uuid.uuid4())
        # Save the file with the unique ID as the filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
        file.save(file_path)
        return jsonify({"id": unique_id}), 200
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/images/<imageId>', methods=['GET'])
def view_image(imageId):
    """Endpoint to view an image by its ID."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], imageId)
    if os.path.exists(file_path):
        # Send the file with the original mimetype preserved
        return send_file(file_path, mimetype='image/*', as_attachment=False)
    else:
        return jsonify({"error": "Image not found"}), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handle internal server errors."""
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found_error(e):
    """Handle not found errors."""
    return jsonify({"error": "Resource not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)