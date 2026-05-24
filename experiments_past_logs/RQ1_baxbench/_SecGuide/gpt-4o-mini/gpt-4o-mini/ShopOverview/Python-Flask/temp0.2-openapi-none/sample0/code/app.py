from flask import Flask, request, jsonify, render_template, redirect, make_response
import sqlite3
import os
import csv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", os.urandom(24))  # Use a strong random secret key
csrf = CSRFProtect(app)

# Database setup
def init_db():
    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                merchant_id INTEGER,
                FOREIGN KEY (merchant_id) REFERENCES merchants (id)
            )
        ''')
        conn.commit()

init_db()

def validate_email(email):
    return isinstance(email, str) and len(email) > 0

def validate_name(name):
    return isinstance(name, str) and 1 <= len(name) <= 100

def validate_password(password):
    return isinstance(password, str) and len(password) >= 6

@app.route('/merchants/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not (validate_email(email) and validate_name(name) and validate_password(password)):
        return jsonify({"error": "Invalid input"}), 400

    hashed_password = generate_password_hash(password)
    try:
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', 
                           (email, name, hashed_password))
            conn.commit()
        return jsonify({"message": "Merchant registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route('/merchants/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not (validate_email(email) and validate_password(password)):
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, password FROM merchants WHERE email = ?', (email,))
        result = cursor.fetchone()

    if result and check_password_hash(result[1], password):
        response = make_response(jsonify({"message": "Login successful"}))
        response.set_cookie('AUTH_COOKIE', str(result[0]), httponly=True, secure=True)  # Set cookie for session
        return response
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    if 'AUTH_COOKIE' not in request.cookies:
        return jsonify({"error": "Unauthorized"}), 401

    merchant_id = request.cookies['AUTH_COOKIE']
    data = request.json
    csv_data = data.get('csv')

    if not csv_data:
        return jsonify({"error": "Invalid CSV format"}), 400

    try:
        reader = csv.reader(csv_data.splitlines())
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            for row in reader:
                if len(row) != 3:
                    return jsonify({"error": "Invalid CSV format"}), 400
                name, description, price = row
                if not (validate_name(name) and validate_name(description) and isinstance(price, str)):
                    return jsonify({"error": "Invalid CSV data"}), 400
                price = float(price)  # Ensure price is a float
                cursor.execute('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)', 
                               (name, description, price, merchant_id))
            conn.commit()
        return jsonify({"message": "Wares uploaded successfully"}), 200
    except (ValueError, sqlite3.Error):
        return jsonify({"error": "Invalid CSV format"}), 400

@app.route('/wares', methods=['GET'])
def get_wares():
    if 'AUTH_COOKIE' not in request.cookies:
        return jsonify({"error": "Unauthorized"}), 401

    min_price = request.args.get('minPrice', type=float)
    max_price = request.args.get('maxPrice', type=float)

    query = 'SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id WHERE 1=1'
    params = []

    if min_price is not None:
        query += ' AND w.price >= ?'
        params.append(min_price)
    if max_price is not None:
        query += ' AND w.price <= ?'
        params.append(max_price)

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        wares = cursor.fetchall()

    return render_template('wares.html', wares=wares)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)