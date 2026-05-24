import os
import sqlite3
from flask import Flask, request, jsonify, make_response, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
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
            merchant_id INTEGER NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/merchants/register', methods=['POST'])
def register_merchant():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'error': 'Invalid input'}), 400

    hashed_password = generate_password_hash(password)
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Merchant registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400

@app.route('/merchants/login', methods=['POST'])
def login_merchant():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, password FROM merchants WHERE email = ?', (email,))
    merchant = cursor.fetchone()
    conn.close()

    if merchant and check_password_hash(merchant[1], password):
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie('AUTH_COOKIE', str(merchant[0]), httponly=True, secure=True)
        return response, 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    merchant_id = request.cookies.get('AUTH_COOKIE')
    if not merchant_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    csv_data = data.get('csv')
    if not csv_data:
        return jsonify({'error': 'Invalid CSV format'}), 400

    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        for line in csv_data.splitlines():
            parts = line.split(',')
            if len(parts) != 3:
                raise ValueError('Invalid CSV format')
            name, description, price = parts
            try:
                price = float(price.strip())
            except ValueError:
                raise ValueError('Invalid price format')
            cursor.execute('INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)', (name.strip(), description.strip(), price, merchant_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Wares uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid CSV format'}), 400

@app.route('/wares', methods=['GET'])
def get_wares():
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

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    wares = cursor.fetchall()
    conn.close()

    html = '''
    <table border="1">
        <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Price</th>
            <th>Merchant Email</th>
        </tr>
        {% for ware in wares %}
        <tr>
            <td>{{ ware[0] }}</td>
            <td>{{ ware[1] }}</td>
            <td>{{ ware[2] }}</td>
            <td>{{ ware[3] }}</td>
        </tr>
        {% endfor %}
    </table>
    '''
    return render_template_string(html, wares=wares)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)