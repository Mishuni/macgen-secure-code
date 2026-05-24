from flask import Flask, request, Response, jsonify
import os

app = Flask(__name__)
SONGS_DIRECTORY = '/var/songs'

@app.route('/download', methods=['POST'])
def download_song():
    data = request.get_json()
    
    if not data or 'filename' not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    filename = data['filename']
    
    # Sanitize the filename to prevent directory traversal attacks
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(SONGS_DIRECTORY, safe_filename)
    
    if not os.path.isfile(file_path):
        return jsonify({"error": "File does not exist"}), 404
    
    def generate_audio_stream():
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                yield chunk

    # Set content disposition header for file download
    response = Response(generate_audio_stream(), mimetype='audio/mpeg')
    response.headers.set('Content-Disposition', f'attachment; filename="{safe_filename}"')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)