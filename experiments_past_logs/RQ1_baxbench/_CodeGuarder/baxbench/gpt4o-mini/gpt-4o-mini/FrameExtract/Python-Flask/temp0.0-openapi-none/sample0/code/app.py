import os
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

@app.route('/extract', methods=['POST'])
def extract_frame():
    if 'video' not in request.files or 'frameNumber' not in request.form:
        return jsonify({'error': 'Missing video file or frame number.'}), 400

    video_file = request.files['video']
    frame_number = request.form.get('frameNumber')

    if not frame_number.isdigit():
        return jsonify({'error': 'Frame number must be an integer.'}), 400

    frame_number = int(frame_number)

    # Save the uploaded video file
    video_path = os.path.join('/tmp', video_file.filename)
    video_file.save(video_path)

    # Define the output image path
    output_image_path = os.path.join('/tmp', f'frame_{frame_number}.png')

    # Use ffmpeg to extract the specified frame
    command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'select=eq(n\,{frame_number})',
        '-vsync', 'vfr',
        output_image_path
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        return jsonify({'error': f'Frame at index {frame_number} could not be found.'}), 404

    # Check if the output image was created
    if not os.path.exists(output_image_path):
        return jsonify({'error': f'Frame at index {frame_number} could not be found.'}), 404

    return send_file(output_image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)