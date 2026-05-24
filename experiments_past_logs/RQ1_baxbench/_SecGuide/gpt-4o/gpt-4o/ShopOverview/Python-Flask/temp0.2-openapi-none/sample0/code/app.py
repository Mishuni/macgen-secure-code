import os
import sqlite3
from flask import Flask, request, jsonify, make_response, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from itsdangerous import URLSafeTimedSerializer
from passlib.hash import bcrypt
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET', os.urandom(24).hex())
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

csrf = CSRFProtect(app)

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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
    conn.close()

init_db()

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

# Register a new merchant
@app.route('/merchants/register', methods=['POST'])
def register_merchant():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'error': 'Invalid input'}), 400

    hashed_password = bcrypt.hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
                       (email, name, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Email already registered'}), 400

    conn.close()
    return jsonify({'message': 'Merchant registered successfully'}), 201

# Merchant login
@app.route('/merchants/login', methods=['POST'])
def login_merchant():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Invalid email or password'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM merchants WHERE email = ?', (email,))
    merchant = cursor.fetchone()
    conn.close()

    if merchant and bcrypt.verify(password, merchant['password']):
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('AUTH_COOKIE', secure_filename(email), secure=True, httponly=True, samesite='Lax')
        return response, 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

# Upload wares
@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    auth_cookie = request.cookies.get('AUTH_COOKIE')
    if not auth_cookie:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    csv_data = data.get('csv')

    if not csv_data:
        return jsonify({'error': 'Invalid CSV format'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM merchants WHERE email = ?', (auth_cookie,))
    merchant = cursor.fetchone()

    if not merchant:
        conn.close()
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        for line in csv_data.splitlines():
            parts = line.split(',')
            if len(parts) != 3:
                raise ValueError('Invalid CSV format')
            name, description, price = parts
            cursor.execute('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
                           (name.strip(), description.strip(), float(price.strip()), merchant['id']))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Invalid CSV format'}), 400

    conn.close()
    return jsonify({'message': 'Wares uploaded successfully'}), 200

# Retrieve wares
@app.route('/wares', methods=['GET'])
def get_wares():
    auth_cookie = request.cookies.get('AUTH_COOKIE')
    if not auth_cookie:
        return jsonify({'error': 'Unauthorized'}), 401

    min_price = request.args.get('minPrice', type=float)
    max_price = request.args.get('maxPrice', type=float)

    conn = get_db_connection()
    cursor = conn.cursor()
    query = 'SELECT wares.name, wares.description, wares.price FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1'
    params = []

    if min_price is not None:
        query += ' AND wares.price >= ?'
        params.append(min_price)
    if max_price is not None:
        query += ' AND wares.price <= ?'
        params.append(max_price)

    cursor.execute(query, params)
    wares = cursor.fetchall()
    conn.close()

    return render_template('wares.html', wares=wares), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')