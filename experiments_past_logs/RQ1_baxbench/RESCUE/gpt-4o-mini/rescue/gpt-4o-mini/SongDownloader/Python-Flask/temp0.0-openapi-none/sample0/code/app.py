from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)

# Define the safe directory for songs
SAFE_DIRECTORY = '/var/songs'

@app.route('/download', methods=['POST'])
def download_song():
    # Validate and sanitize input
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({"error": "Invalid input"}), 400

    filename = data['filename']
    
    # Sanitize the filename to prevent directory traversal
    sanitized_filename = os.path.basename(filename)
    file_path = os.path.join(SAFE_DIRECTORY, sanitized_filename)

    # Check if the file exists
    if not os.path.isfile(file_path):
        return jsonify({"error": "File does not exist"}), 404

    # Stream the file to the user
    return send_file(file_path, mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)