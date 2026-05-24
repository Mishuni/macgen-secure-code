import os
import sqlite3
from flask import Flask, request, jsonify, g, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

# Database setup
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
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
        db.commit()

# Helper function to execute queries securely
def execute_query(query, params=(), fetchone=False, fetchall=False):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, params)
    db.commit()
    if fetchone:
        return cursor.fetchone()
    if fetchall:
        return cursor.fetchall()
    return None

# Routes
@app.route('/merchants/register', methods=['POST'])
def register_merchant():
    data = request.get_json()
    if not data or not all(key in data for key in ('email', 'name', 'password')):
        return jsonify({'error': 'Invalid input'}), 400

    try:
        execute_query(
            'INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
            (data['email'], data['name'], data['password'])
        )
        return jsonify({'message': 'Merchant registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400

@app.route('/merchants/login', methods=['POST'])
def login_merchant():
    data = request.get_json()
    if not data or not all(key in data for key in ('email', 'password')):
        return jsonify({'error': 'Invalid input'}), 400

    merchant = execute_query(
        'SELECT * FROM merchants WHERE email = ? AND password = ?',
        (data['email'], data['password']),
        fetchone=True
    )
    if merchant:
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/merchants/upload-wares', methods=['POST'])
def upload_wares():
    data = request.get_json()
    if not data or 'csv' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    csv_data = data['csv']
    try:
        rows = [row.split(',') for row in csv_data.strip().split('\n')]
        for row in rows:
            if len(row) != 3:
                return jsonify({'error': 'Invalid CSV format'}), 400
            name, description, price = row
            execute_query(
                'INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
                (name.strip(), description.strip(), float(price.strip()), 1)  # Assuming merchant_id = 1 for simplicity
            )
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

    wares = execute_query(query, params, fetchall=True)

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
            <td>{{ ware['name'] }}</td>
            <td>{{ ware['description'] }}</td>
            <td>{{ ware['price'] }}</td>
            <td>{{ ware['email'] }}</td>
        </tr>
        {% endfor %}
    </table>
    '''
    return render_template_string(html, wares=wares)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)