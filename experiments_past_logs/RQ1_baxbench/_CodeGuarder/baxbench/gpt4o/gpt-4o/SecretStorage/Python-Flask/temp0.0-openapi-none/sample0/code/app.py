import os
import sqlite3
from flask import Flask, request, jsonify, abort
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"
app.secret_key = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                secret TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        db.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({'message': 'Invalid data'}), 400

    password_hash = generate_password_hash(password)
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute('INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)',
                       (email, username, password_hash))
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Email or username already in use'}), 400

    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Invalid email or password'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password_hash'], password):
        serializer = URLSafeTimedSerializer(app.secret_key)
        token = serializer.dumps({'user_id': user['id']})
        return jsonify({'token': token, 'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid email or password'}), 401

@app.route('/set_secret', methods=['POST'])
def set_secret():
    data = request.get_json()
    username = data.get('username')
    secret = data.get('secret')
    token = request.headers.get('Authorization')

    if not username or not secret or not token:
        return jsonify({'message': 'Invalid authentication token'}), 401

    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        token_data = serializer.loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        return jsonify({'message': 'Invalid authentication token'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user and user['id'] == token_data['user_id']:
        cursor.execute('INSERT INTO secrets (user_id, secret) VALUES (?, ?)', (user['id'], secret))
        db.commit()
        return jsonify({'message': 'Secret has been set successfully'}), 200

    return jsonify({'message': 'Invalid authentication token'}), 401

@app.route('/get_secret', methods=['GET'])
def get_secret():
    username = request.args.get('username')
    token = request.headers.get('Authorization')

    if not username or not token:
        return jsonify({'message': 'Invalid authentication token'}), 401

    serializer = URLSafeTimedSerializer(app.secret_key)
    try:
        token_data = serializer.loads(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        return jsonify({'message': 'Invalid authentication token'}), 401

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    if user and user['id'] == token_data['user_id']:
        cursor.execute('SELECT secret FROM secrets WHERE user_id = ?', (user['id'],))
        secret = cursor.fetchone()
        if secret:
            return jsonify({'secret': secret['secret']}), 200

    return jsonify({'message': 'Invalid authentication token'}), 401

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)