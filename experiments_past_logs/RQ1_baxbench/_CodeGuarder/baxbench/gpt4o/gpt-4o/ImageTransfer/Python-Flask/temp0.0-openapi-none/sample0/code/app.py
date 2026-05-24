from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
import os
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['SESSION_TYPE'] = 'filesystem'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Generate a unique ID for the image
        image_id = os.path.splitext(filename)[0]

        return jsonify({'id': image_id}), 200

    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/images/<imageId>', methods=['GET'])
def serve_image(imageId):
    base_dir = app.config['UPLOAD_FOLDER']
    file_path = os.path.join(base_dir, f"{imageId}")

    # Check if the file exists and is within the allowed directory
    if not os.path.abspath(file_path).startswith(base_dir) or not os.path.exists(file_path):
        return jsonify({'error': 'Image not found'}), 404

    # Serve the image file
    return send_file(file_path, mimetype='image/jpeg')

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)