from flask import Flask, request, jsonify, send_file, render_template_string
import sqlite3
import os
import io
import html

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT,
                profile_photo BLOB
            )
        ''')
        conn.commit()

@app.route('/add_profile', methods=['POST'])
def add_profile():
    username = request.form.get('username')
    profile_page = request.form.get('profile_page')
    profile_photo = request.files.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return jsonify({'error': 'Invalid input'}), 400

    # Validate file type
    if not profile_photo.filename.endswith('.png'):
        return jsonify({'error': 'Profile photo must be a PNG file'}), 400

    # Read the profile photo
    profile_photo_data = profile_photo.read()

    # Sanitize the profile page content to prevent XSS
    profile_page = html.escape(profile_page)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                           (username, profile_page, profile_photo_data))
            conn.commit()
            return jsonify({'message': 'Profile created successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Profile already exists, creation forbidden'}), 403

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
        profile = cursor.fetchone()
        if profile:
            return render_template_string(profile[0]), 200
        else:
            return jsonify({'error': 'Profile not found'}), 404

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
        profile_photo = cursor.fetchone()
        if profile_photo:
            return send_file(
                io.BytesIO(profile_photo[0]),
                mimetype='image/png'
            ), 200
        else:
            return jsonify({'error': 'Profile photo not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)