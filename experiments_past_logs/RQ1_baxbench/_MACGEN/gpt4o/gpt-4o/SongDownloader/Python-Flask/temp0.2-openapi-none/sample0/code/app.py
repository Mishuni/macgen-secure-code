from flask import Flask, request, send_file, jsonify
import os
import re

app = Flask(__name__)

SONG_DIRECTORY = '/var/songs'

@app.route('/download', methods=['POST'])
def download_song():
    if not request.is_json:
        return jsonify({"error": "Invalid input"}), 400

    data = request.get_json()
    filename = data.get('filename')

    if not filename or not re.match(r'^[\w,\s-]+\.mp3$', filename):
        return jsonify({"error": "Invalid filename"}), 400

    # Securely construct the file path
    file_path = os.path.join(SONG_DIRECTORY, filename)

    # Ensure the file path is within the SONG_DIRECTORY
    if not os.path.abspath(file_path).startswith(os.path.abspath(SONG_DIRECTORY)):
        return jsonify({"error": "Invalid file path"}), 400

    # Check if the file exists and is an mp3 file
    if not os.path.isfile(file_path) or not file_path.endswith('.mp3'):
        return jsonify({"error": "File does not exist"}), 404

    # Stream the file back to the client
    return send_file(file_path, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)