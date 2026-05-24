from flask import Flask, request, jsonify, send_file
import subprocess
import os

app = Flask(__name__)

@app.route('/create-gif', methods=['POST'])
def create_gif():
    if 'images' not in request.files:
        return jsonify({'error': 'No images provided'}), 400

    images = request.files.getlist('images')
    target_size = request.form.get('targetSize')
    delay = request.form.get('delay', default=10, type=int)
    append_reverted = request.form.get('appendReverted', default='false').lower() == 'true'

    if not target_size:
        return jsonify({'error': 'Target size is required'}), 400

    try:
        width, height = map(int, target_size.split('x'))
    except ValueError:
        return jsonify({'error': 'Invalid target size format. Use width x height.'}), 400

    temp_images = []
    for img in images:
        if img.filename == '':
            return jsonify({'error': 'One or more images have no filename'}), 400
        temp_img_path = f"/tmp/{img.filename}"
        img.save(temp_img_path)
        temp_images.append(temp_img_path)

    gif_path = "/tmp/output.gif"
    convert_command = ['convert', '-delay', str(delay), '-resize', f'{width}x{height}'] + temp_images + [gif_path]

    try:
        subprocess.run(convert_command, check=True)

        if append_reverted:
            reversed_images = list(reversed(temp_images))
            convert_command_reversed = ['convert', '-delay', str(delay), '-resize', f'{width}x{height}'] + reversed_images + [gif_path]
            subprocess.run(convert_command_reversed, check=True)

        return send_file(gif_path, mimetype='image/gif')

    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to create GIF'}), 500
    finally:
        for img_path in temp_images:
            if os.path.exists(img_path):
                os.remove(img_path)
        if os.path.exists(gif_path):
            os.remove(gif_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)