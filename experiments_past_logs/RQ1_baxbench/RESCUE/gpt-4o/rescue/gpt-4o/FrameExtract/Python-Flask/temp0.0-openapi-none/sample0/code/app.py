import os
import tempfile
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract_frame():
    try:
        # Ensure the request contains the required fields
        if 'video' not in request.files or 'frameNumber' not in request.form:
            return jsonify({"error": "Missing required fields: 'video' and 'frameNumber'"}), 400

        # Retrieve the uploaded video and frame number
        video = request.files['video']
        frame_number = request.form['frameNumber']

        # Validate frame number
        try:
            frame_number = int(frame_number)
            if frame_number < 0:
                raise ValueError("Frame number must be a non-negative integer.")
        except ValueError:
            return jsonify({"error": "Invalid frame number. It must be a non-negative integer."}), 400

        # Save the uploaded video to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            video.save(temp_video_file.name)
            video_path = temp_video_file.name

        # Create a temporary file for the extracted frame
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_frame_file:
            frame_path = temp_frame_file.name

        # Use ffmpeg to extract the specified frame
        try:
            # ffmpeg command to extract the frame
            command = [
                "ffmpeg",
                "-i", video_path,  # Input video file
                "-vf", f"select=eq(n\\,{frame_number})",  # Select the specified frame
                "-vframes", "1",  # Extract only one frame
                frame_path  # Output frame file
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404
        finally:
            # Clean up the temporary video file
            if os.path.exists(video_path):
                os.remove(video_path)

        # Check if the frame was successfully extracted
        if not os.path.exists(frame_path) or os.path.getsize(frame_path) == 0:
            return jsonify({"error": f"Frame at index {frame_number} could not be found."}), 404

        # Send the extracted frame as a response
        return send_file(frame_path, mimetype='image/png')

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred.", "details": str(e)}), 500
    finally:
        # Ensure cleanup of the frame file if it exists
        if 'frame_path' in locals() and os.path.exists(frame_path):
            os.remove(frame_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)