from flask import Flask, request, jsonify, send_file, abort
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not file.content_type.startswith('image/'):
        return jsonify({'error': 'Invalid file type'}), 400
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
        return jsonify({'error': 'Invalid file extension'}), 400
    try:
        image_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_FOLDER, image_id)
        file.save(file_path)
        return jsonify({'id': image_id}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<imageId>', methods=['GET'])
def get_image(imageId):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, imageId)
        if not os.path.exists(file_path):
            return jsonify({'error': 'Image not found'}), 404
        return send_file(file_path, mimetype='image/*', as_attachment=False)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)