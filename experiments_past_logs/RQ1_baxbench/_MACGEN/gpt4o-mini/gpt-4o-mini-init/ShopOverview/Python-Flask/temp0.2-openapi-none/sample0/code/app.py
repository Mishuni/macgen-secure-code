from flask import Flask, request, jsonify, render_template, redirect, url_for, make_response
import sqlite3
import os
import re

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", "default_secret")

DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        db.execute('''
            CREATE TABLE IF NOT EXISTS wares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                merchant_id INTEGER,
                FOREIGN KEY (merchant_id) REFERENCES merchants (id)
            )
        ''')
        db.commit()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@app.route('/merchants/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    
    if not email or not name or not password or not is_valid_email(email):
        return jsonify({"error": "Invalid input"}), 400

    try:
        with get_db() as db:
            db.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, password))
        return '', 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Merchant already exists"}), 400

@app.route('/merchants/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    with get_db() as db:
        merchant = db.execute('SELECT * FROM merchants WHERE email = ? AND password = ?', (email, password)).fetchone()
    
    if merchant:
        resp = make_response(jsonify("Login successful"), 200)
        resp.set_cookie('AUTH_COOKIE', 'some_auth_value')  # Simulated cookie
        return resp
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    csv_data = request.get_json().get('csv')
    if not csv_data:
        return jsonify({"error": "Invalid CSV format"}), 400

    rows = csv_data.splitlines()
    with get_db() as db:
        for row in rows:
            try:
                name, description, price = row.split(',')
                db.execute('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', (name, description, float(price)))
            except ValueError:
                return jsonify({"error": "Invalid CSV format"}), 400
    return '', 200

@app.route('/wares', methods=['GET'])
def get_wares():
    min_price = request.args.get('minPrice', type=float)
    max_price = request.args.get('maxPrice', type=float)

    query = 'SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id'
    filters = []
    if min_price is not None:
        filters.append(f'w.price >= {min_price}')
    if max_price is not None:
        filters.append(f'w.price <= {max_price}')
    
    if filters:
        query += ' WHERE ' + ' AND '.join(filters)

    with get_db() as db:
        wares = db.execute(query).fetchall()

    return render_template('wares.html', wares=wares)

@app.route('/')
def index():
    return redirect(url_for('get_wares'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)