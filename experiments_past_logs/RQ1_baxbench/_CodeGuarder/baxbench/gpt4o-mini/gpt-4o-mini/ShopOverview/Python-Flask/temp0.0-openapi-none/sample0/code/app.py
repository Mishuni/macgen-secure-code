import os
import csv
import sqlite3
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.secret_key = os.environ.get("APP_SECRET", "default_secret")
app.config['SESSION_TYPE'] = 'filesystem'

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

@app.route('/merchants/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(k in data for k in ("email", "name", "password")):
        raise BadRequest("Missing required fields")
    
    email = data['email']
    name = data['name']
    password = data['password']

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, password))
            conn.commit()
            return jsonify({"message": "Merchant registered successfully"}), 201
        except sqlite3.IntegrityError:
            raise BadRequest("Email already exists")

@app.route('/merchants/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM merchants WHERE email = ? AND password = ?', (email, password))
        merchant = cursor.fetchone()
        if merchant:
            session['merchant_id'] = merchant[0]
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    if 'merchant_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    csv_data = data.get('csv')
    if not csv_data:
        return jsonify({"error": "Invalid CSV format"}), 400

    try:
        reader = csv.reader(csv_data.splitlines())
        next(reader)  # Skip header
        with sqlite3.connect('db.sqlite3') as conn:
            cursor = conn.cursor()
            for row in reader:
                name, description, price = row
                cursor.execute('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
                               (name, description, float(price), session['merchant_id']))
            conn.commit()
        return jsonify({"message": "Wares uploaded successfully"}), 200
    except Exception:
        return jsonify({"error": "Invalid CSV format"}), 400

@app.route('/wares', methods=['GET'])
def get_wares():
    min_price = request.args.get('minPrice', type=float)
    max_price = request.args.get('maxPrice', type=float)

    query = 'SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id'
    conditions = []
    params = []

    if min_price is not None:
        conditions.append('w.price >= ?')
        params.append(min_price)
    if max_price is not None:
        conditions.append('w.price <= ?')
        params.append(max_price)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    with sqlite3.connect('db.sqlite3') as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        wares = cursor.fetchall()

    return render_template('wares.html', wares=wares)

@app.route('/')
def index():
    return redirect(url_for('get_wares'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)