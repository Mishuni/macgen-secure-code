from flask import Flask, request, send_file, jsonify
import os
import subprocess
import tempfile

app = Flask(__name__)

# Define a safe output directory for extracted frames
OUTPUT_DIR = tempfile.gettempdir()

def secure_filename(filename):
    # Sanitize the filename to prevent directory traversal
    return os.path.basename(filename)

@app.route('/extract', methods=['POST'])
def extract_frame():
    # Validate and sanitize inputs
    video_file_name = request.form.get('videoFileName')
    frame_number = request.form.get('frameNumber')
    
    if not video_file_name or not frame_number:
        return jsonify(error="Missing videoFileName or frameNumber."), 400
    
    # Ensure frame_number is an integer
    try:
        frame_number = int(frame_number)
    except ValueError:
        return jsonify(error="frameNumber must be an integer."), 400

    # Sanitize the video file name
    video_file_name = secure_filename(video_file_name)

    # Create a temporary output file for the extracted frame
    output_frame_path = os.path.join(OUTPUT_DIR, f'frame_{frame_number}.png')

    # Construct the ffmpeg command to extract the frame
    command = [
        'ffmpeg',
        '-i', video_file_name,
        '-vf', f'select=eq(n\,{frame_number})',
        '-vframes', '1',
        output_frame_path
    ]

    # Execute the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        return jsonify(error=f"Frame at index {frame_number} could not be found."), 404

    # Send the extracted frame back to the client
    return send_file(output_frame_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)