from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import os
import mimetypes

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
TEMP_DIR = 'temp_images'
GIF_OUTPUT = 'output.gif'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_FILES = 10

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_content(file):
    mime_type, _ = mimetypes.guess_type(file.filename)
    return mime_type and mime_type.startswith('image/')

@app.route('/create-gif', methods=['POST'])
def create_gif():
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400

    images = request.files.getlist('images')
    if len(images) > MAX_FILES:
        return jsonify({'error': f'You can upload a maximum of {MAX_FILES} images.'}), 400

    target_size = request.form.get('targetSize')
    delay = request.form.get('delay', default=10, type=int)
    append_reverted = request.form.get('appendReverted', default=False, type=bool)

    if not target_size:
        return jsonify({'error': 'Target size is required'}), 400

    # Validate target_size format
    if not validate_target_size(target_size):
        return jsonify({'error': 'Invalid target size format. Use "WIDTHxHEIGHT".'}), 400

    # Create a temporary directory to store images
    os.makedirs(TEMP_DIR, exist_ok=True)

    image_paths = []
    try:
        for i, image in enumerate(images):
            if image and allowed_file(image.filename):
                if image.content_length > MAX_FILE_SIZE:
                    return jsonify({'error': 'File size exceeds the maximum limit of 5 MB.'}), 400

                if not validate_file_content(image):
                    return jsonify({'error': 'Uploaded file is not a valid image.'}), 400

                filename = secure_filename(image.filename)
                image_path = os.path.join(TEMP_DIR, f'image_{i}.png')
                image.save(image_path)
                image_paths.append(image_path)
            else:
                return jsonify({'error': 'Invalid file type. Only images are allowed.'}), 400

        # Create the GIF using Pillow
        images_to_convert = [Image.open(img_path).resize(parse_target_size(target_size)) for img_path in image_paths]
        images_to_convert[0].save(GIF_OUTPUT, save_all=True, append_images=images_to_convert[1:], duration=delay * 100, loop=0)

        if append_reverted:
            images_to_convert.reverse()
            images_to_convert[0].save(GIF_OUTPUT, save_all=True, append_images=images_to_convert[1:], duration=delay * 100, loop=0)

        return send_file(GIF_OUTPUT, mimetype='image/gif')

    except Exception as e:
        return jsonify({'error': 'An error occurred while processing the images.'}), 500

    finally:
        # Clean up temporary images
        for image_path in image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
        if os.path.exists(GIF_OUTPUT):
            os.remove(GIF_OUTPUT)
        if os.path.exists(TEMP_DIR):
            os.rmdir(TEMP_DIR)

def validate_target_size(size):
    try:
        width, height = map(int, size.split('x'))
        return width > 0 and height > 0
    except ValueError:
        return False

def parse_target_size(size):
    width, height = map(int, size.split('x'))
    return (width, height)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)