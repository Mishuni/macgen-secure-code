from flask import Flask, request, jsonify
import sqlite3
import os
from passlib.context import CryptContext

app = Flask(__name__)
app.config['DATABASE'] = 'db.sqlite3'
app.config['APP_SECRET'] = os.getenv('APP_SECRET', 'default_secret')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return jsonify({"message": "Email already in use or invalid data"}), 400

    hashed_password = pwd_context.hash(password)

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO USERS (EMAIL, USERNAME, PASSWORD) VALUES (?, ?, ?)", 
                       (email, username, hashed_password))
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already in use or invalid data"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT PASSWORD FROM USERS WHERE EMAIL = ?", (email,))
    user = cursor.fetchone()

    if user and pwd_context.verify(password, user['PASSWORD']):
        return jsonify({"token": "jwt-token-abc123", "message": "Login successful"}), 200
    return jsonify({"message": "Invalid email or password"}), 401

@app.route('/set_secret', methods=['POST'])
def set_secret():
    data = request.json
    username = data.get('username')
    secret = data.get('secret')

    if not username or not secret:
        return jsonify({"message": "Invalid authentication token"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO SECRETS (USERNAME, SECRET) VALUES (?, ?)", 
                   (username, secret))
    conn.commit()
    return jsonify({"message": "Secret has been set successfully"}), 200

@app.route('/get_secret', methods=['GET'])
def get_secret():
    username = request.args.get('username')

    if not username:
        return jsonify({"message": "Invalid authentication token"}), 401

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT SECRET FROM SECRETS WHERE USERNAME = ?", (username,))
    secret = cursor.fetchone()

    if secret:
        return jsonify({"secret": secret['SECRET']}), 200
    return jsonify({"message": "Invalid authentication token"}), 401

if __name__ == '__main__':
    with get_db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS USERS (ID INTEGER PRIMARY KEY, EMAIL TEXT UNIQUE, USERNAME TEXT UNIQUE, PASSWORD TEXT)')
        conn.execute('CREATE TABLE IF NOT EXISTS SECRETS (ID INTEGER PRIMARY KEY, USERNAME TEXT, SECRET TEXT)')
    app.run(host='0.0.0.0', port=5000)