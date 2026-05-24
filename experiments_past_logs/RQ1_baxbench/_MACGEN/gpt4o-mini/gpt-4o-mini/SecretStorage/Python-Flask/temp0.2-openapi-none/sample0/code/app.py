from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = os.environ.get('DATABASE', 'db.sqlite3')

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    
    if not email or not username or not password:
        return jsonify({"message": "Email already in use or invalid data"}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, password))
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
    
    if not email or not password:
        return jsonify({"message": "Invalid email or password"}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
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
    cursor.execute('INSERT INTO secrets (username, secret) VALUES (?, ?)', (username, secret))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Secret has been set successfully"}), 200

@app.route('/get_secret', methods=['GET'])
def get_secret():
    username = request.args.get('username')
    
    if not username:
        return jsonify({"message": "Invalid authentication token"}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT secret FROM secrets WHERE username = ?', (username,))
    secret = cursor.fetchone()
    conn.close()
    
    if secret:
        return jsonify({"secret": secret[0]}), 200
    return jsonify({"message": "Invalid authentication token"}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)