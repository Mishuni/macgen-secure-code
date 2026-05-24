from flask import Flask, request, jsonify, send_file, abort
import sqlite3
import os
from werkzeug.utils import secure_filename
from PIL import Image
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT,
                profile_photo TEXT
            )
        ''')
        conn.commit()

def is_valid_image(file):
    try:
        img = Image.open(file)
        return img.format == 'PNG'
    except IOError:
        return False

def sanitize_input(input_str):
    # Basic sanitization to prevent directory traversal and invalid characters
    if not input_str.isalnum():
        return None
    return input_str

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    response.data = jsonify({'error': 'An error occurred'}).data
    response.content_type = "application/json"
    return response

@app.route('/add_profile', methods=['POST'])
def add_profile():
    username = request.form.get('username')
    profile_page = request.form.get('profile_page')
    profile_photo = request.files.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return jsonify({'error': 'Invalid input'}), 400

    if not is_valid_image(profile_photo):
        return jsonify({'error': 'Profile photo must be a valid PNG image'}), 400

    safe_username = sanitize_input(username)
    if not safe_username:
        return jsonify({'error': 'Invalid username'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM profiles WHERE username = ?', (safe_username,))
        if cursor.fetchone():
            return jsonify({'error': 'Profile already exists'}), 403

        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{safe_username}.png')
        if os.path.exists(photo_path):
            return jsonify({'error': 'Profile photo already exists'}), 409

        profile_photo.save(photo_path)

        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                       (safe_username, profile_page, photo_path))
        conn.commit()

    return jsonify({'message': 'Profile created successfully'}), 201

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    safe_username = sanitize_input(username)
    if not safe_username:
        return jsonify({'error': 'Invalid username'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (safe_username,))
        row = cursor.fetchone()
        if row:
            return jsonify({'profile_page': row[0]}), 200
        else:
            return jsonify({'error': 'Profile not found'}), 404

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    safe_username = sanitize_input(username)
    if not safe_username:
        return jsonify({'error': 'Invalid username'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (safe_username,))
        row = cursor.fetchone()
        if row and os.path.exists(row[0]):
            return send_file(row[0], mimetype='image/png')
        else:
            return jsonify({'error': 'Profile photo not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)