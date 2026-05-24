from flask import Flask, request, send_file, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_frame():
    if 'video' not in request.files or 'frameNumber' not in request.form:
        return jsonify({"error": "Invalid input"}), 400

    video = request.files['video']
    frame_number = request.form['frameNumber']

    try:
        frame_number = int(frame_number)
    except ValueError:
        return jsonify({"error": "Frame number must be an integer"}), 400

    if frame_number < 0:
        return jsonify({"error": "Frame number must be non-negative"}), 400

    filename = secure_filename(video.filename)
    video_path = os.path.join('/tmp', filename)
    video.save(video_path)

    output_image_path = os.path.join('/tmp', f"frame_{frame_number}.png")

    try:
        command = [
            'ffmpeg', '-i', video_path, '-vf', f"select=eq(n\,{frame_number})",
            '-vframes', '1', output_image_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(output_image_path):
            raise FileNotFoundError

        return send_file(output_image_path, mimetype='image/png')

    except (subprocess.CalledProcessError, FileNotFoundError):
        return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_image_path):
            os.remove(output_image_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)