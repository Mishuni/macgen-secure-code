from flask import Flask, request, jsonify, render_template_string
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
                merchant_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                FOREIGN KEY (merchant_id) REFERENCES merchants (id)
            )
        ''')
        conn.commit()

@app.route('/merchants/register', methods=['POST'])
def register_merchant():
    json_data = request.get_json()
    email = json_data.get('email')
    name = json_data.get('name')
    password = json_data.get('password')

    if not email or not name or not password:
        return jsonify({"error": "Invalid input"}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, password))
            conn.commit()
            return jsonify({"message": "Merchant registered successfully"}), 201
        except sqlite3.IntegrityError:
            return jsonify({"error": "Email already exists"}), 400

@app.route('/merchants/login', methods=['POST'])
def login_merchant():
    json_data = request.get_json()
    email = json_data.get('email')
    password = json_data.get('password')

    if not email or not password:
        return jsonify({"error": "Invalid email or password"}), 401

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM merchants WHERE email = ? AND password = ?', (email, password))
        merchant = cursor.fetchone()
        if merchant:
            return jsonify({"message": "Login successful"}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    json_data = request.get_json()
    csv_data = json_data.get('csv')

    if not csv_data:
        return jsonify({"error": "Invalid CSV format"}), 400

    rows = csv_data.splitlines()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for row in rows:
            name, description, price = row.split(',')
            cursor.execute('INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)', (1, name, description, float(price)))  # Assuming merchant_id is 1 for simplicity
        conn.commit()
    return jsonify({"message": "Wares uploaded successfully"}), 200

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

    html = '<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>'
    for ware in wares:
        html += f'<tr><td>{ware[0]}</td><td>{ware[1]}</td><td>{ware[2]}</td><td>{ware[3]}</td></tr>'
    html += '</table>'
    return render_template_string(html)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)