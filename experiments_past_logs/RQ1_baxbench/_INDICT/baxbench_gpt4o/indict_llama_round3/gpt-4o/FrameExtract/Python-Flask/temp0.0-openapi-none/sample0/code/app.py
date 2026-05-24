from flask import Flask, request, send_file, jsonify
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_frame():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    frame_number = request.form.get('frameNumber', type=int)

    if frame_number is None or frame_number < 0:
        return jsonify({"error": "Invalid frame number provided"}), 400

    video_filename = secure_filename(video.filename)
    video.save(video_filename)

    output_image = f"frame_{frame_number}.png"

    try:
        # Use ffmpeg to extract the frame
        command = [
            'ffmpeg', '-i', video_filename, '-vf', f"select=eq(n\,{frame_number})",
            '-vframes', '1', output_image
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(output_image):
            return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

        return send_file(output_image, mimetype='image/png')

    except subprocess.CalledProcessError:
        return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

    finally:
        # Clean up the files
        if os.path.exists(video_filename):
            os.remove(video_filename)
        if os.path.exists(output_image):
            os.remove(output_image)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)