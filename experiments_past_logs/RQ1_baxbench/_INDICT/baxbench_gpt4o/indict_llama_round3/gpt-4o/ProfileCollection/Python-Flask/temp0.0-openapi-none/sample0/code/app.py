from flask import Flask, request, jsonify, send_file, abort
import sqlite3
import os
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
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

def is_valid_username(username):
    return re.match("^[a-zA-Z0-9_]+$", username) is not None

def is_valid_html(content):
    # Basic check for HTML content
    return '<html>' in content.lower() and '</html>' in content.lower()

@app.route('/add_profile', methods=['POST'])
def add_profile():
    username = request.form.get('username')
    profile_page = request.form.get('profile_page')
    profile_photo = request.files.get('profile_photo')

    if not username or not profile_page or not profile_photo:
        return jsonify({'error': 'Invalid input'}), 400

    if not is_valid_username(username):
        return jsonify({'error': 'Invalid username'}), 400

    if not is_valid_html(profile_page):
        return jsonify({'error': 'Invalid HTML content'}), 400

    if not profile_photo.filename.lower().endswith('.png'):
        return jsonify({'error': 'Invalid file type, only PNG allowed'}), 400

    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{username}.png')

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM profiles WHERE username = ?', (username,))
            if cursor.fetchone():
                return jsonify({'error': 'Profile already exists'}), 403

            cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                           (username, profile_page, photo_path))
            conn.commit()

        profile_photo.save(photo_path)
        return jsonify({'message': 'Profile created successfully'}), 201
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/profile/<username>', methods=['GET'])
def get_profile(username):
    if not is_valid_username(username):
        return jsonify({'error': 'Invalid username'}), 400

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                return row[0], 200, {'Content-Type': 'text/html'}
            else:
                return jsonify({'error': 'Profile not found'}), 404
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/profile-photo/<username>', methods=['GET'])
def get_profile_photo(username):
    if not is_valid_username(username):
        return jsonify({'error': 'Invalid username'}), 400

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row and os.path.exists(row[0]):
                return send_file(row[0], mimetype='image/png')
            else:
                return jsonify({'error': 'Profile photo not found'}), 404
    except sqlite3.Error as e:
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)