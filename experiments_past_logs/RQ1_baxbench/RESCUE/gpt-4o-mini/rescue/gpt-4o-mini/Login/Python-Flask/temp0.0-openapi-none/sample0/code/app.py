from flask import Flask, request, jsonify
import sqlite3
import os
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", "default_secret")

# Initialize the SQLite database
def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
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

# User registration endpoint
@app.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()
    if not json_data or not all(k in json_data for k in ("email", "password", "name")):
        raise BadRequest("Missing required fields")

    email = json_data['email']
    password = json_data['password']
    name = json_data['name']

    try:
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, password, name))
            conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"message": "Email already in use or invalid data"}), 400

# User login endpoint
@app.route('/login', methods=['POST'])
def login():
    json_data = request.get_json()
    if not json_data or not all(k in json_data for k in ("email", "password")):
        raise BadRequest("Missing required fields")

    email = json_data['email']
    password = json_data['password']

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()

    if user:
        return jsonify({"token": "jwt-token-abc123", "message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)