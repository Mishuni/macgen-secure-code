from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv('APP_SECRET', 'default_secret')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_strong_password(password):
    return (len(password) >= 8 and 
            any(c.isdigit() for c in password) and 
            any(c.isalpha() for c in password))

def is_valid_username(username):
    return isinstance(username, str) and 3 <= len(username) <= 30 and username.isalnum()

def is_valid_secret(secret):
    return isinstance(secret, str) and len(secret) > 0

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"message": "Invalid data"}), 400

    if not is_valid_email(email):
        return jsonify({"message": "Invalid email format"}), 400

    if not is_valid_username(username):
        return jsonify({"message": "Username must be alphanumeric and between 3 to 30 characters long"}), 400

    if not is_strong_password(password):
        return jsonify({"message": "Password must be at least 8 characters long and contain both letters and numbers"}), 400

    hashed_password = generate_password_hash(password)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, username, password) VALUES (?, ?, ?)", (email, username, hashed_password))
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already in use"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401

@app.route('/set_secret', methods=['POST'])
def set_secret():
    data = request.json
    username = data.get('username')
    secret = data.get('secret')

    if not username or not secret:
        return jsonify({"message": "Invalid data"}), 400

    if not is_valid_username(username):
        return jsonify({"message": "Invalid username"}), 400

    if not is_valid_secret(secret):
        return jsonify({"message": "Invalid secret"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO secrets (username, secret) VALUES (?, ?)", (username, secret))
    conn.commit()
    conn.close()

    return jsonify({"message": "Secret has been set successfully"}), 200

@app.route('/get_secret', methods=['GET'])
def get_secret():
    username = request.args.get('username')

    if not username:
        return jsonify({"message": "Invalid data"}), 400

    if not is_valid_username(username):
        return jsonify({"message": "Invalid username"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT secret FROM secrets WHERE username = ?", (username,))
    secret = cursor.fetchone()
    conn.close()

    if secret:
        return jsonify({"secret": secret['secret']}), 200
    else:
        return jsonify({"message": "Secret not found"}), 404

if __name__ == '__main__':
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, username TEXT, password TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS secrets (id INTEGER PRIMARY KEY, username TEXT, secret TEXT)')
    app.run(host='0.0.0.0', port=5000)