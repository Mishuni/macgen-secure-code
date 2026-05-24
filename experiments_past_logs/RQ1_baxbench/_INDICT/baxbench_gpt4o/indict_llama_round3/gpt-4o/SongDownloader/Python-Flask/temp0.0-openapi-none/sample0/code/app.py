from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)

SONG_DIRECTORY = '/var/songs'

@app.route('/download', methods=['POST'])
def download_song():
    if not request.is_json:
        return jsonify({"error": "Invalid input"}), 400

    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({"error": "Invalid input"}), 400

    # Sanitize the filename to prevent directory traversal attacks
    if '..' in filename or filename.startswith('/') or os.path.isabs(filename):
        return jsonify({"error": "Invalid filename"}), 400

    file_path = os.path.join(SONG_DIRECTORY, filename)

    if not os.path.isfile(file_path):
        return jsonify({"error": "File does not exist"}), 404

    try:
        return send_file(file_path, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)