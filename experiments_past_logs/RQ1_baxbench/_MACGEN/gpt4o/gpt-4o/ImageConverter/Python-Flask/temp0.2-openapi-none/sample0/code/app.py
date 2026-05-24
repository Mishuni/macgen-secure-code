from flask import Flask, request, send_file, jsonify
import os
import subprocess
import re
from werkzeug.utils import secure_filename
from tempfile import TemporaryDirectory

app = Flask(__name__)

def validate_target_size(target_size):
    return re.match(r'^\d+x\d+$', target_size) is not None

@app.route('/create-gif', methods=['POST'])
def create_gif():
    try:
        # Validate request
        if 'images' not in request.files:
            return jsonify({'error': 'No images part in the request'}), 400
        
        images = request.files.getlist('images')
        target_size = request.form.get('targetSize')
        delay = request.form.get('delay', default=10, type=int)
        append_reverted = request.form.get('appendReverted', default='false').lower() == 'true'

        if not target_size or not validate_target_size(target_size):
            return jsonify({'error': 'Invalid target size format. Expected format: widthxheight'}), 400

        if delay <= 0:
            return jsonify({'error': 'Delay must be a positive integer'}), 400

        # Create a temporary directory to store images
        with TemporaryDirectory() as temp_dir:
            image_paths = []
            for image in images:
                filename = secure_filename(image.filename)
                image_path = os.path.join(temp_dir, filename)
                image.save(image_path)
                image_paths.append(image_path)

            # Prepare the ImageMagick command
            output_gif_path = os.path.join(temp_dir, 'output.gif')
            command = ['convert', '-delay', str(delay), '-resize', target_size]

            # Add images to the command
            command.extend(image_paths)

            # Append reverted images if required
            if append_reverted:
                command.extend(reversed(image_paths))

            # Specify the output file
            command.append(output_gif_path)

            # Execute the command
            subprocess.run(command, check=True)

            # Return the generated GIF
            return send_file(output_gif_path, mimetype='image/gif')

    except subprocess.CalledProcessError:
        return jsonify({'error': 'Failed to create GIF'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)