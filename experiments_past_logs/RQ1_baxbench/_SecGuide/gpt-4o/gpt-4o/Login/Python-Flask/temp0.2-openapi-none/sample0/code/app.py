import os
import sqlite3
from flask import Flask, request, jsonify, g, abort
from passlib.hash import pbkdf2_sha256
from werkzeug.security import safe_str_cmp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET', 'default_secret_key')
app.config['DATABASE'] = os.environ.get('DATABASE_PATH', 'db.sqlite3')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize rate limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    db.commit()

def get_user_by_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    return cursor.fetchone()

def add_user(email, password, name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, password, name))
    db.commit()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_password(password):
    return len(password) >= 8 and re.search(r"[A-Z]", password) and re.search(r"[a-z]", password) and re.search(r"[0-9]", password) and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)

@app.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return jsonify({'message': 'Invalid data'}), 400

    if not is_valid_email(email):
        return jsonify({'message': 'Invalid email format'}), 400

    if get_user_by_email(email):
        return jsonify({'message': 'Registration failed'}), 400

    if not is_valid_password(password):
        return jsonify({'message': 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character'}), 400

    hashed_password = pbkdf2_sha256.hash(password)
    add_user(email, hashed_password, name)
    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Invalid email or password'}), 401

    user = get_user_by_email(email)
    if user and pbkdf2_sha256.verify(password, user[2]):
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'message': 'Invalid email or password'}), 401

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')