from flask import Flask, request, jsonify
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.config['DATABASE'] = 'db.sqlite3'
app.config['APP_SECRET'] = os.environ.get('APP_SECRET', 'your_default_secret')  # Ensure APP_SECRET is set
app.config['WTF_CSRF_SECRET_KEY'] = os.urandom(24)  # CSRF protection
csrf = CSRFProtect(app)

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

def validate_password(password):
    return len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isalpha() for char in password)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'message': 'Invalid data'}), 400

    if not validate_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if not validate_password(password):
        return jsonify({'message': 'Password must be at least 8 characters long and contain both letters and numbers'}), 400

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Specify a strong hashing algorithm

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                       (email, hashed_password, name))
        conn.commit()
        return jsonify({'message': 'Registration successful'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'An error occurred. Please try again.'}), 400  # Generic error message
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Invalid email or password'}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)