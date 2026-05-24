from flask import Flask, request, jsonify, send_file, abort
import os

app = Flask(__name__)

# Configuration for session storage
app.config['SESSION_TYPE'] = "filesystem"

BASE_DIR = '/var/songs'

@app.route('/download', methods=['POST'])
def download_song():
    data = request.get_json()
    
    # Validate input
    if not data or 'filename' not in data or not isinstance(data['filename'], str):
        return jsonify({"error": "Invalid input"}), 400

    filename = data['filename']
    
    # Sanitize filename to prevent directory traversal
    safe_filename = os.path.basename(filename)
    full_path = os.path.join(BASE_DIR, safe_filename)

    # Check if the file exists
    if not os.path.isfile(full_path):
        return jsonify({"error": "File does not exist"}), 404

    # Stream the file back to the client
    return send_file(full_path, mimetype='audio/mpeg', as_attachment=True, download_name=safe_filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)