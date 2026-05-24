import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

# Initialize SQLite database
DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
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

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        if not email or not password or not name:
            return jsonify({"message": "Invalid data"}), 400

        # Insert user into the database
        try:
            execute_query(
                "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                (email, password, name)
            )
            return jsonify({"message": "Registration successful"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"message": "Email already in use"}), 400
    except Exception as e:
        return jsonify({"message": "An error occurred"}), 500

# Route for user login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"message": "Invalid email or password"}), 401

        # Fetch user from the database
        user = execute_query(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password),
            fetchone=True
        )

        if user:
            return jsonify({
                "token": "jwt-token-placeholder",
                "message": "Login successful"
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"message": "An error occurred"}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)