from flask import Flask, request, jsonify, send_file
import subprocess
import os
import tempfile
import mimetypes
import magic  # python-magic for MIME type checking

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_frame():
    if 'video' not in request.files or 'frameNumber' not in request.form:
        return jsonify(error="Missing video file or frame number."), 400

    video_file = request.files['video']
    frame_number = request.form['frameNumber']

    # Validate frame number
    try:
        frame_number = int(frame_number)
        if frame_number < 0:
            raise ValueError
    except ValueError:
        return jsonify(error="Invalid frame number."), 400

    # Validate the file type
    if not video_file or not allowed_file(video_file.filename):
        return jsonify(error="Invalid file type."), 400

    # Check the MIME type of the uploaded file
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(video_file.read())
    video_file.seek(0)  # Reset file pointer after reading
    if not mime_type.startswith('video/'):
        return jsonify(error="Uploaded file is not a valid video."), 400

    # Create a secure temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        video_path = os.path.join(temp_dir, secure_filename(video_file.filename))
        video_file.save(video_path)

        # Define the output image path
        output_image_path = os.path.join(temp_dir, f"frame_{frame_number}.png")

        # Use ffmpeg to extract the frame
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', f'select=eq(n\,{frame_number})',
            '-vsync', 'vfr',
            output_image_path
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return jsonify(error="Frame extraction failed."), 500

        # Check if the output image was created
        if not os.path.exists(output_image_path):
            return jsonify(error="Frame could not be found."), 404

        # Dynamically determine the MIME type of the output image
        mime_type = mimetypes.guess_type(output_image_path)[0] or 'image/png'

        # Send the extracted frame back to the user
        return send_file(output_image_path, mimetype=mime_type)

def allowed_file(filename):
    # Check if the file has a valid video extension
    allowed_extensions = {'mp4', 'avi', 'mov', 'mkv'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def secure_filename(filename):
    # Generate a secure filename by removing any path components
    return os.path.basename(filename)

@app.route('/')
def index():
    return "Welcome to FrameExtract API. Use POST /extract to extract frames."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)