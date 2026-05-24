from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'db.sqlite3'

# Initialize the SQLite database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
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

@app.route('/merchants/register', methods=['POST'])
def register_merchant():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'error': 'Invalid input'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, password))
            conn.commit()
            return '', 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Merchant already exists'}), 400

@app.route('/merchants/login', methods=['POST'])
def login_merchant():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM merchants WHERE email = ? AND password = ?', (email, password))
        merchant = cursor.fetchone()
        if merchant:
            response = jsonify('Login successful')
            response.set_cookie('AUTH_COOKIE', 'some_secure_value')  # Set a cookie for session management
            return response, 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    data = request.json
    csv_data = data.get('csv')

    if not csv_data:
        return jsonify({'error': 'Invalid CSV format'}), 400

    rows = csv_data.splitlines()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for row in rows:
            try:
                name, description, price = row.split(',')
                cursor.execute('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)', (name, description, float(price)))
            except ValueError:
                return jsonify({'error': 'Invalid CSV format'}), 400
        conn.commit()
    return '', 200

@app.route('/wares', methods=['GET'])
def get_wares():
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

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        wares = cursor.fetchall()

    return render_template('wares.html', wares=wares)

@app.route('/')
def index():
    return 'Welcome to the Merchant WebApp API!'

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)