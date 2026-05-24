from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
import os
import subprocess
import tempfile

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/create-gif', methods=['POST'])
def create_gif():
    try:
        # Validate and handle request data
        if 'images' not in request.files:
            return jsonify({'error': 'No images part in the request'}), 400

        images = request.files.getlist('images')
        target_size = request.form.get('targetSize')
        delay = request.form.get('delay', default=10, type=int)
        append_reverted = request.form.get('appendReverted', default=False, type=lambda x: x.lower() == 'true')

        if not target_size:
            return jsonify({'error': 'Target size is required'}), 400

        # Create a temporary directory to store images
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []
            for image in images:
                filename = secure_filename(image.filename)
                image_path = os.path.join(temp_dir, filename)
                image.save(image_path)
                image_paths.append(image_path)

            # Prepare the command for ImageMagick
            gif_path = os.path.join(temp_dir, 'output.gif')
            command = ['convert', '-delay', str(delay), '-resize', target_size] + image_paths

            if append_reverted:
                command += list(reversed(image_paths))

            command.append(gif_path)

            # Execute the command
            subprocess.run(command, check=True)

            # Return the generated GIF
            return send_file(gif_path, mimetype='image/gif')

    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to create GIF'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)