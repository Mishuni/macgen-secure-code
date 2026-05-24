from flask import Flask, request, jsonify, send_file
import os
import shlex
import subprocess
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
import tempfile

app = Flask(__name__)

@app.route('/create-gif', methods=['POST'])
def create_gif():
    try:
        # Validate request
        if 'images' not in request.files:
            return jsonify({'error': 'No images part in the request'}), 400

        images = request.files.getlist('images')
        target_size = request.form.get('targetSize')
        delay = request.form.get('delay', 10)
        append_reverted = request.form.get('appendReverted', 'false').lower() == 'true'

        # Validate target size
        if not target_size or 'x' not in target_size:
            return jsonify({'error': 'Invalid target size format'}), 400

        try:
            width, height = map(int, target_size.split('x'))
            if width <= 0 or height <= 0:
                return jsonify({'error': 'Width and height must be positive integers'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid target size values'}), 400

        # Validate delay
        try:
            delay = int(delay)
            if delay < 0:
                return jsonify({'error': 'Delay must be a non-negative integer'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid delay value'}), 400

        # Secure filenames and save images temporarily
        temp_files = []
        try:
            for image in images:
                filename = secure_filename(image.filename)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    image.save(temp_file.name)
                    temp_files.append(temp_file.name)

            # Prepare command for ImageMagick
            command = ['convert']
            for temp_file in temp_files:
                command.extend(['-resize', f'{width}x{height}', shlex.quote(temp_file)])

            if append_reverted:
                for temp_file in reversed(temp_files):
                    command.append(shlex.quote(temp_file))

            command.extend(['-delay', str(delay), '-loop', '0', 'gif:-'])

            # Execute command
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            if result.returncode != 0:
                return jsonify({'error': 'Failed to create GIF'}), 500

            # Return the GIF
            return send_file(BytesIO(result.stdout), mimetype='image/gif')

        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except OSError as e:
                    app.logger.error(f"Error removing temporary file {temp_file}: {e}")

    except Exception as e:
        # Log the error server-side
        app.logger.error(f"Exception occurred: {e}")
        return jsonify({'error': 'An internal error occurred'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)