from flask import Flask, request, jsonify, send_file
import os
import subprocess
import re

app = Flask(__name__)

def validate_target_size(target_size):
    # Validate the target size format (width x height)
    pattern = re.compile(r'^\d+x\d+$')
    if not pattern.match(target_size):
        raise ValueError("Invalid target size format. Use 'widthxheight'.")

def validate_delay(delay):
    if not isinstance(delay, int) or delay < 0:
        raise ValueError("Delay must be a non-negative integer.")

@app.route('/create-gif', methods=['POST'])
def create_gif():
    # Check if the request contains files
    if 'images' not in request.files:
        return jsonify({"error": "No images provided."}), 400

    images = request.files.getlist('images')
    target_size = request.form.get('targetSize')
    delay = request.form.get('delay', default=10, type=int)
    append_reverted = request.form.get('appendReverted', default=False, type=bool)

    try:
        # Validate inputs
        validate_target_size(target_size)
        validate_delay(delay)

        # Create a temporary directory to store images
        temp_dir = 'temp_images'
        os.makedirs(temp_dir, exist_ok=True)

        image_paths = []
        for image in images:
            if image and image.filename:
                # Save the uploaded images to the temporary directory
                image_path = os.path.join(temp_dir, image.filename)
                image.save(image_path)
                image_paths.append(image_path)

        # Create the GIF using ImageMagick
        gif_path = 'output.gif'
        convert_command = ['convert', '-delay', str(delay), '-resize', target_size] + image_paths + [gif_path]

        if append_reverted:
            # Append the reversed images
            convert_command += ['(', *reversed(image_paths), ')']

        subprocess.run(convert_command, check=True)

        # Send the generated GIF back to the client
        return send_file(gif_path, mimetype='image/gif')

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error: " + str(e)}), 500
    finally:
        # Clean up temporary files
        for image_path in image_paths:
            if os.path.exists(image_path):
                os.remove(image_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)