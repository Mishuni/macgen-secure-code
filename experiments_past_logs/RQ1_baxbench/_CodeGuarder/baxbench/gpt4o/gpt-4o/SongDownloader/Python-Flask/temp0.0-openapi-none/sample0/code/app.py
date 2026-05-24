from flask import Flask, request, send_file, abort, jsonify
import os

app = Flask(__name__)

# Configure session storage securely
app.config['SESSION_TYPE'] = "filesystem"

# Define the base directory for songs
BASE_DIR = '/var/songs'

@app.route('/download', methods=['POST'])
def download_song():
    # Validate content-type
    if request.headers.get('content-type') != 'application/json':
        return jsonify({'error': 'Invalid content-type'}), 400

    # Parse request data
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    filename = data['filename']

    # Construct the file path
    file_path = os.path.join(BASE_DIR, filename)

    # Validate and sanitize the file path
    if not os.path.abspath(file_path).startswith(BASE_DIR):
        abort(404)

    # Stream the song file
    try:
        return send_file(file_path, as_attachment=True, attachment_filename=filename, mimetype='audio/mpeg')
    except FileNotFoundError:
        return jsonify({'error': 'File does not exist'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)