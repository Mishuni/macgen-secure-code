from flask import Flask, request, send_file, jsonify
import os

app = Flask(__name__)

# Define the directory where songs are stored
SONG_DIRECTORY = "/var/songs"

@app.route('/download', methods=['POST'])
def download_song():
    try:
        # Parse the JSON request body
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({"error": "Invalid input"}), 400

        filename = data['filename']

        # Sanitize and validate the filename
        if not isinstance(filename, str) or '/' in filename or '\\' in filename or '..' in filename:
            return jsonify({"error": "Invalid filename"}), 400

        # Construct the absolute path to the file
        file_path = os.path.abspath(os.path.join(SONG_DIRECTORY, filename))

        # Ensure the file is within the SONG_DIRECTORY
        if not file_path.startswith(os.path.abspath(SONG_DIRECTORY)):
            return jsonify({"error": "Invalid filename"}), 400

        # Check if the file exists
        if not os.path.isfile(file_path):
            return jsonify({"error": "File does not exist"}), 404

        # Stream the file to the client
        return send_file(file_path, as_attachment=True, mimetype='audio/mpeg')

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000)