from flask import Flask, request, send_file, jsonify
import os
import subprocess
import tempfile
import werkzeug.utils
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_talisman import Talisman

app = Flask(__name__)

# Apply security headers using Flask-Talisman
Talisman(app)

# Fix for proxy setups
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/extract', methods=['POST'])
def extract_frame():
    if 'video' not in request.files or 'frameNumber' not in request.form:
        return jsonify({"error": "Invalid input"}), 400

    video = request.files['video']
    frame_number = request.form.get('frameNumber', type=int)

    if not video or frame_number is None:
        return jsonify({"error": "Invalid input"}), 400

    # Validate the content type of the uploaded file
    if not video.mimetype.startswith('video/'):
        return jsonify({"error": "Uploaded file is not a video"}), 400

    # Validate that frame_number is a non-negative integer
    if frame_number < 0:
        return jsonify({"error": "Frame number must be a non-negative integer"}), 400

    # Create a temporary directory to store the uploaded video
    with tempfile.TemporaryDirectory() as temp_dir:
        # Securely generate a filename
        video_filename = werkzeug.utils.secure_filename(video.filename)
        video_path = os.path.join(temp_dir, video_filename)
        video.save(video_path)

        # Define the output path for the extracted frame
        output_frame_path = os.path.join(temp_dir, 'frame.png')

        # Use ffmpeg to extract the specified frame
        try:
            subprocess.run(
                ['ffmpeg', '-i', video_path, '-vf', f'select=eq(n\,{frame_number})', '-vframes', '1', output_frame_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError as e:
            # Log the error details for debugging (not exposed to the user)
            app.logger.error(f"FFmpeg error: {e.stderr.decode()}")
            return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

        # Check if the frame was successfully extracted
        if not os.path.exists(output_frame_path):
            return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

        # Send the extracted frame as a response
        return send_file(output_frame_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)