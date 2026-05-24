from flask import Flask, request, jsonify, send_file
import os
import subprocess

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_frame():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided."}), 400

    video_file = request.files['video']
    frame_number = request.form.get('frameNumber', type=int)

    if not video_file or frame_number is None:
        return jsonify({"error": "Invalid input."}), 400

    video_file_name = video_file.filename
    video_file_path = os.path.join('/tmp', video_file_name)
    video_file.save(video_file_path)

    output_image_path = os.path.join('/tmp', f'frame_{frame_number}.png')

    # Use ffmpeg to extract the frame
    command = [
        'ffmpeg',
        '-i', video_file_path,
        '-vf', f'select=eq(n\,{frame_number})',
        '-vsync', 'vfr',
        output_image_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        os.remove(video_file_path)
        return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

    if not os.path.exists(output_image_path):
        os.remove(video_file_path)
        return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

    # Cleanup temporary files
    os.remove(video_file_path)

    return send_file(output_image_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)