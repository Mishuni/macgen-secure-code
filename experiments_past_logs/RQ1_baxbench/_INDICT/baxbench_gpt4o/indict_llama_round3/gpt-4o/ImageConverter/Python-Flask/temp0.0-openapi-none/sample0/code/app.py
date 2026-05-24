from flask import Flask, request, send_file, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename
from tempfile import TemporaryDirectory

app = Flask(__name__)

@app.route('/create-gif', methods=['POST'])
def create_gif():
    if 'images' not in request.files:
        return jsonify({'error': 'No images part in the request'}), 400

    images = request.files.getlist('images')
    target_size = request.form.get('targetSize')
    delay = request.form.get('delay', default=10, type=int)
    append_reverted = request.form.get('appendReverted', default='false').lower() == 'true'

    if not target_size:
        return jsonify({'error': 'Target size is required'}), 400

    try:
        width, height = map(int, target_size.lower().split('x'))
    except ValueError:
        return jsonify({'error': 'Invalid target size format. Use WIDTHxHEIGHT'}), 400

    # Limit the number of images to prevent DoS attacks
    if len(images) > 20:
        return jsonify({'error': 'Too many images. Maximum allowed is 20.'}), 400

    with TemporaryDirectory() as temp_dir:
        image_paths = []
        for i, image in enumerate(images):
            filename = secure_filename(f'image_{i}.png')
            filepath = os.path.join(temp_dir, filename)
            image.save(filepath)
            image_paths.append(filepath)

        if append_reverted:
            image_paths.extend(reversed(image_paths))

        output_gif_path = os.path.join(temp_dir, 'output.gif')
        convert_command = [
            'convert',
            '-delay', str(delay),
            '-resize', f'{width}x{height}',
            *image_paths,
            output_gif_path
        ]

        try:
            subprocess.run(convert_command, check=True, shell=False)
        except subprocess.CalledProcessError:
            return jsonify({'error': 'Failed to create GIF'}), 500

        return send_file(output_gif_path, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)