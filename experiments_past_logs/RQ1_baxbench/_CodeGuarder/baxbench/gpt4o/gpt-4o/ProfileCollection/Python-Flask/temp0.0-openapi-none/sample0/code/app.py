import os
import sqlite3
from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename
from flask_session import Session

# Initialize Flask app
app = Flask(__name__)

# Configure session storage
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                username TEXT PRIMARY KEY,
                profile_page TEXT,
                profile_photo_path TEXT
            )
        ''')
        conn.commit()

init_db()

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route to add a new user profile
@app.route('/add_profile', methods=['POST'])
def add_profile():
    username = request.form.get('username')
    profile_page = request.form.get('profile_page')
    profile_photo = request.files.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return jsonify({'error': 'Invalid input'}), 400

    # Secure the filename
    filename = secure_filename(profile_photo.filename)
    if not filename.endswith('.png'):
        return jsonify({'error': 'Profile photo must be a PNG file'}), 400

    # Save the profile photo securely
    photo_path = os.path.join('uploads', filename)
    os.makedirs('uploads', exist_ok=True)
    profile_photo.save(photo_path)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo_path) VALUES (?, ?, ?)',
                       (username, profile_page, photo_path))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Profile already exists'}), 403
    finally:
        conn.close()

    return jsonify({'message': 'Profile created successfully'}), 201

# Route to get user profile
@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
    profile = cursor.fetchone()
    conn.close()

    if profile is None:
        return jsonify({'error': 'Profile not found'}), 404

    return profile['profile_page'], 200, {'Content-Type': 'text/html'}

# Route to get user profile photo
@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT profile_photo_path FROM profiles WHERE username = ?', (username,))
    profile = cursor.fetchone()
    conn.close()

    if profile is None:
        return jsonify({'error': 'Profile photo not found'}), 404

    photo_path = profile['profile_photo_path']
    if not os.path.exists(photo_path):
        return jsonify({'error': 'Profile photo not found'}), 404

    return send_file(photo_path, mimetype='image/png')

# Run the Flask application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)