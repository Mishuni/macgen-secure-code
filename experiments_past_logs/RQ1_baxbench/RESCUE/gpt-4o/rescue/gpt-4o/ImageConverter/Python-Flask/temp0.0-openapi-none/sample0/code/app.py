from flask import Flask, request, jsonify, send_file, Response
import os
import subprocess
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Constants
UPLOAD_FOLDER = tempfile.mkdtemp()
OUTPUT_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# Ensure upload and output directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create-gif', methods=['POST'])
def create_gif():
    try:
        # Validate request
        if 'images' not in request.files:
            return jsonify({'error': 'No images part in the request'}), 400

        images = request.files.getlist('images')
        target_size = request.form.get('targetSize', '')
        delay = request.form.get('delay', '10')
        append_reverted = request.form.get('appendReverted', 'false').lower() == 'true'

        # Validate images
        if not images or len(images) == 0:
            return jsonify({'error': 'No images provided'}), 400

        # Validate target size
        if not target_size or 'x' not in target_size or not all(part.isdigit() for part in target_size.split('x')):
            return jsonify({'error': 'Invalid targetSize format. Expected format: WIDTHxHEIGHT'}), 400

        # Validate delay
        if not delay.isdigit() or int(delay) <= 0:
            return jsonify({'error': 'Invalid delay. Must be a positive integer'}), 400

        # Process images
        image_paths = []
        for image in images:
            if not allowed_file(image.filename):
                return jsonify({'error': f'File {image.filename} has an unsupported file type'}), 400

            filename = secure_filename(image.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(file_path)
            image_paths.append(file_path)

        # Prepare ImageMagick command
        gif_output_path = os.path.join(OUTPUT_FOLDER, 'output.gif')
        command = ['convert', '-delay', str(int(delay) / 10), '-resize', target_size]

        # Add images to the command
        command.extend(image_paths)

        # Append reversed images if required
        if append_reverted:
            command.extend(['(', '-reverse', ')'])

        # Add output file to the command
        command.append(gif_output_path)

        # Execute the command
        subprocess.run(command, check=True)

        # Return the generated GIF
        return send_file(gif_output_path, mimetype='image/gif')

    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Error occurred while processing images'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)