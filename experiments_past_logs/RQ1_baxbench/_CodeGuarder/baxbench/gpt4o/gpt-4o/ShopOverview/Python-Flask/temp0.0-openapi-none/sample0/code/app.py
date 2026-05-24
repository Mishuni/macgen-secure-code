import os
import sqlite3
from flask import Flask, request, jsonify, make_response, abort, send_file, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from passlib.hash import bcrypt
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET', 'default_secret')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_PERMANENT'] = False

# Database setup
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS wares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id INTEGER NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    return conn

def validate_csv(csv_string):
    try:
        csv_reader = csv.reader(io.StringIO(csv_string))
        for row in csv_reader:
            if len(row) != 3:
                return False
        return True
    except Exception:
        return False

# Routes
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
    try:
        conn.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    finally:
        conn.close()

    return jsonify({'message': 'Merchant registered successfully'}), 201

@app.route('/merchants/login', methods=['POST'])
def login_merchant():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Invalid email or password'}), 401

    conn = get_db_connection()
    merchant = conn.execute('SELECT * FROM merchants WHERE email = ?', (email,)).fetchone()
    conn.close()

    if merchant and bcrypt.verify(password, merchant['password']):
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('AUTH_COOKIE', email, httponly=True, secure=True)
        return response

    return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    if 'AUTH_COOKIE' not in request.cookies:
        return jsonify({'error': 'Unauthorized'}), 401

    email = request.cookies.get('AUTH_COOKIE')
    conn = get_db_connection()
    merchant = conn.execute('SELECT * FROM merchants WHERE email = ?', (email,)).fetchone()

    if not merchant:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    csv_string = data.get('csv')

    if not csv_string or not validate_csv(csv_string):
        return jsonify({'error': 'Invalid CSV format'}), 400

    csv_reader = csv.reader(io.StringIO(csv_string))
    for row in csv_reader:
        name, description, price = row
        conn.execute('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
                     (name, description, float(price), merchant['id']))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Wares uploaded successfully'}), 200

@app.route('/wares', methods=['GET'])
def retrieve_wares():
    if 'AUTH_COOKIE' not in request.cookies:
        return jsonify({'error': 'Unauthorized'}), 401

    min_price = request.args.get('minPrice', type=float)
    max_price = request.args.get('maxPrice', type=float)

    query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1'
    params = []

    if min_price is not None:
        query += ' AND wares.price >= ?'
        params.append(min_price)
    if max_price is not None:
        query += ' AND wares.price <= ?'
        params.append(max_price)

    conn = get_db_connection()
    wares = conn.execute(query, params).fetchall()
    conn.close()

    html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>'
    for ware in wares:
        html += f'<tr><td>{ware["name"]}</td><td>{ware["description"]}</td><td>{ware["price"]}</td><td>{ware["email"]}</td></tr>'
    html += '</table>'

    return render_template_string(html), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)