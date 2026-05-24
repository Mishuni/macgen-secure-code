from flask import Flask, request, jsonify
import sqlite3
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/add', methods=['POST'])
def add_product():
    if not request.is_json:
        return jsonify({'error': 'Invalid input'}), 400
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    additional_data = {k: v for k, v in data.items() if k != 'name'}
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, json.dumps(additional_data)))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Product already exists'}), 400
    finally:
        conn.close()
    return jsonify({'message': 'Product successfully added'}), 201

@app.route('/download', methods=['GET'])
def download_product():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({'data': row[0]}), 200
    return jsonify({'error': 'Product not found'}), 400

@app.route('/upload', methods=['POST'])
def upload_product():
    if not request.is_json:
        return jsonify({'error': 'Invalid upload query'}), 400
    data = request.get_json()
    name = data.get('name')
    product_data = data.get('data')
    if not name or not product_data:
        return jsonify({'error': 'Name and data are required'}), 400
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET data = ? WHERE name = ?', (product_data, name))
    if cursor.rowcount == 0:
        return jsonify({'error': 'Product not found'}), 400
    conn.commit()
    conn.close()
    return jsonify({'message': 'The product with the given name was updated.'}), 200

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Invalid search query'}), 400
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()
    results = [{'name': row[0], **json.loads(row[1])} for row in rows]
    return jsonify({'results': results}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)