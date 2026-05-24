from flask import Flask, request, jsonify, send_file
import os
import subprocess
import tempfile

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/create-gif', methods=['POST'])
def create_gif():
    # Validate input
    if 'images' not in request.files or 'targetSize' not in request.form:
        return jsonify({'error': 'Missing required fields: images and targetSize'}), 400

    images = request.files.getlist('images')
    target_size = request.form['targetSize']
    delay = request.form.get('delay', default=10, type=int)
    append_reverted = request.form.get('appendReverted', default=False, type=bool)

    # Validate target size
    try:
        width, height = map(int, target_size.split('x'))
    except ValueError:
        return jsonify({'error': 'Invalid targetSize format. Use width x height.'}), 400

    # Create a temporary directory to store images
    with tempfile.TemporaryDirectory() as temp_dir:
        image_paths = []
        for image in images:
            if image.filename == '':
                return jsonify({'error': 'Empty image filename'}), 400
            image_path = os.path.join(temp_dir, image.filename)
            image.save(image_path)
            image_paths.append(image_path)

        # Prepare the convert command
        convert_command = ['convert']
        convert_command.extend(image_paths)
        convert_command.append('-resize')
        convert_command.append(f'{width}x{height}')
        convert_command.append('-delay')
        convert_command.append(str(delay))
        output_gif_path = os.path.join(temp_dir, 'output.gif')
        convert_command.append(output_gif_path)

        # Execute the convert command
        try:
            subprocess.run(convert_command, check=True)
            if append_reverted:
                reversed_gif_path = os.path.join(temp_dir, 'reversed.gif')
                convert_command_reversed = ['convert']
                convert_command_reversed.append('-delay')
                convert_command_reversed.append(str(delay))
                convert_command_reversed.append('-reverse')
                convert_command_reversed.append(output_gif_path)
                convert_command_reversed.append(reversed_gif_path)
                subprocess.run(convert_command_reversed, check=True)
                # Append the reversed GIF to the original
                with open(output_gif_path, 'ab') as original_gif, open(reversed_gif_path, 'rb') as reversed_gif:
                    original_gif.write(reversed_gif.read())

            return send_file(output_gif_path, mimetype='image/gif')
        except subprocess.CalledProcessError as e:
            return jsonify({'error': 'Error during GIF creation: ' + str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)