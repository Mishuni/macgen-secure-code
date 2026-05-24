import os
import sqlite3
from flask import Flask, request, jsonify
from passlib.hash import pbkdf2_sha256
import jwt
from datetime import datetime, timedelta
from werkzeug.security import safe_str_cmp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re

app = Flask(__name__)

# Use a strong, unique secret key
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'your-secure-secret-key')

DATABASE = 'db.sqlite3'

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_password(password):
    # Implement a stronger password policy
    return (len(password) >= 8 and
            re.search(r"[A-Z]", password) and
            re.search(r"[a-z]", password) and
            re.search(r"[0-9]", password) and
            re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({'message': 'Invalid data'}), 400

    if not validate_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if not validate_password(password):
        return jsonify({'message': 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character'}), 400

    hashed_password = pbkdf2_sha256.hash(password)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
                       (email, username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Registration successful'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Registration failed'}), 400

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Invalid email or password'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and pbkdf2_sha256.verify(password, user['password']):
        token = jwt.encode({'username': user['username'], 'exp': datetime.utcnow() + timedelta(hours=1)},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token, 'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/set_secret', methods=['POST'])
@limiter.limit("10 per minute")
def set_secret():
    data = request.get_json()
    username = data.get('username')
    secret = data.get('secret')
    auth_header = request.headers.get('Authorization')

    if not auth_header or not username or not secret:
        return jsonify({'message': 'Invalid authentication token'}), 401

    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if not safe_str_cmp(decoded['username'], username):
            return jsonify({'message': 'Invalid authentication token'}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid authentication token'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO secrets (username, secret) VALUES (?, ?)', (username, secret))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Secret has been set successfully'}), 200

@app.route('/get_secret', methods=['GET'])
@limiter.limit("10 per minute")
def get_secret():
    username = request.args.get('username')
    auth_header = request.headers.get('Authorization')

    if not auth_header or not username:
        return jsonify({'message': 'Invalid authentication token'}), 401

    token = auth_header.split(" ")[1] if " " in auth_header else auth_header

    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        if not safe_str_cmp(decoded['username'], username):
            return jsonify({'message': 'Invalid authentication token'}), 401
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid authentication token'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT secret FROM secrets WHERE username = ?', (username,))
    secret = cursor.fetchone()
    conn.close()

    if secret:
        return jsonify({'secret': secret['secret']}), 200
    else:
        return jsonify({'message': 'No secret found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)