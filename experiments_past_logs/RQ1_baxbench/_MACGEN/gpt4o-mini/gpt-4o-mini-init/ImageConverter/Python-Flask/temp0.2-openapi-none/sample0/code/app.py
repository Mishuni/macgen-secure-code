from flask import Flask, request, jsonify, send_file
import os
import subprocess
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)

MAX_IMAGES = 10
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

@app.route('/create-gif', methods=['POST'])
def create_gif():
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400

    images = request.files.getlist('images')
    target_size = request.form.get('targetSize')
    delay = request.form.get('delay', default=10, type=int)
    append_reverted = request.form.get('appendReverted', default=False, type=bool)

    if not target_size or not re.match(r'^\d+x\d+$', target_size):
        return jsonify({'error': 'Invalid target size format. Use widthxheight.'}), 400

    if len(images) > MAX_IMAGES:
        return jsonify({'error': f'Cannot upload more than {MAX_IMAGES} images.'}), 400

    total_size = sum(len(image.read()) for image in images)
    if total_size > MAX_UPLOAD_SIZE:
        return jsonify({'error': 'Total upload size exceeds the limit of 5 MB.'}), 400

    image_files = []
    for image in images:
        if image and image.filename:
            filename = secure_filename(image.filename)
            filepath = os.path.join('/tmp', filename)
            image.save(filepath)
            image_files.append(filepath)

    gif_filename = '/tmp/output.gif'
    convert_command = ['convert', '-delay', str(delay), '-resize', target_size] + image_files + [gif_filename]

    try:
        subprocess.run(convert_command, check=True)

        if append_reverted:
            reversed_gif_filename = '/tmp/reversed.gif'
            reversed_command = ['convert', '-delay', str(delay), '-resize', target_size] + list(reversed(image_files)) + [reversed_gif_filename]
            subprocess.run(reversed_command, check=True)
            subprocess.run(['convert', gif_filename, reversed_gif_filename, '-append', gif_filename], check=True)
            os.remove(reversed_gif_filename)

        for file in image_files:
            os.remove(file)

        return send_file(gif_filename, mimetype='image/gif')

    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Error creating GIF: ' + str(e)}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)