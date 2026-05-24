import os
import tempfile
import subprocess
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/extract', methods=['POST'])
def extract_frame():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file part'}), 400

    video = request.files['video']
    frame_number = request.form.get('frameNumber', type=int)

    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(video.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    if frame_number is None or frame_number < 0:
        return jsonify({'error': 'Invalid frame number'}), 400

    filename = secure_filename(video.filename)
    video_path = os.path.join(UPLOAD_FOLDER, filename)
    video.save(video_path)

    frame_filename = f"frame_{frame_number}.png"
    frame_path = os.path.join(UPLOAD_FOLDER, frame_filename)

    try:
        command = [
            'ffmpeg', '-i', video_path, '-vf', f'select=eq(n\,{frame_number})',
            '-vframes', '1', frame_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(frame_path):
            return jsonify({'error': f'Frame at index {frame_number} could not be found.'}), 404

        return send_file(frame_path, mimetype='image/png')

    except subprocess.CalledProcessError:
        return jsonify({'error': f'Frame at index {frame_number} could not be found.'}), 404

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(frame_path):
            os.remove(frame_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)