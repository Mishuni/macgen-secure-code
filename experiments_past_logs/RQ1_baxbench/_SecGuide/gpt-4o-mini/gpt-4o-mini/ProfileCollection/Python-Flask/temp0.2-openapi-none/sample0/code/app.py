from flask import Flask, request, jsonify, render_template, send_file, abort
import sqlite3
import os
import io
from PIL import Image
import re

app = Flask(__name__)
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

# Initialize the SQLite database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT NOT NULL,
                profile_photo BLOB NOT NULL
            )
        ''')
        conn.commit()

def is_valid_username(username):
    # Improved validation for username (e.g., alphanumeric and length)
    return re.match(r'^[a-zA-Z0-9]{1,30}$', username) is not None

def validate_image(file):
    try:
        img = Image.open(file)
        img.verify()  # Verify that it is an image
        return True
    except Exception:
        return False

@app.route('/add_profile', methods=['POST'])
def add_profile():
    username = request.form.get('username')
    profile_page = request.form.get('profile_page')
    profile_photo = request.files.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return jsonify({'error': 'Invalid input'}), 400

    if not is_valid_username(username):
        return jsonify({'error': 'Invalid username'}), 400

    # Check file extension and validate image
    if not (profile_photo.filename.endswith('.png') and validate_image(profile_photo)):
        return jsonify({'error': 'Profile photo must be a valid PNG image'}), 400

    # Limit file size to 1MB
    if profile_photo.content_length > 1 * 1024 * 1024:
        return jsonify({'error': 'File size exceeds limit of 1MB'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                           (username, profile_page, profile_photo.read()))
            conn.commit()
            return jsonify({'message': 'Profile created successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Profile already exists, creation forbidden'}), 403

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    if not is_valid_username(username):
        return jsonify({'error': 'Invalid username'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        profile = cursor.fetchone()
        if profile:
            return render_template('profile_template.html', profile_page=profile[0])
        else:
            return jsonify({'error': 'Profile not found'}), 404

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    if not is_valid_username(username):
        return jsonify({'error': 'Invalid username'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        photo = cursor.fetchone()
        if photo:
            return send_file(
                io.BytesIO(photo[0]),
                mimetype='image/png',
                as_attachment=False,
                attachment_filename=f"{username}.png"
            )
        else:
            return jsonify({'error': 'Profile photo not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)