from flask import Flask, request, jsonify
import sqlite3
import os
import json

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add', methods=['POST'])
def add_product():
    data = request.get_json()
    if not isinstance(data, dict) or 'name' not in data:
        return jsonify({'error': 'Invalid input'}), 400

    name = data['name']
    additional_properties = {k: v for k, v in data.items() if k != 'name'}

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO products (name, properties) VALUES (?, ?)", (name, json.dumps(additional_properties)))
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
        return jsonify({'error': 'Invalid input'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT properties FROM products WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({'data': row['properties']}), 200
    else:
        return jsonify({'error': 'Product not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_product():
    data = request.get_json()
    if not isinstance(data, dict) or 'name' not in data or 'data' not in data:
        return jsonify({'error': 'Invalid upload query'}), 400

    name = data['name']
    properties = data['data']

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE products SET properties = ? WHERE name = ?", (properties, name))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Product not found'}), 404
        conn.commit()
    finally:
        conn.close()

    return jsonify({'message': 'The product with the given name was updated.'}), 200

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Invalid search query'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, properties FROM products")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        properties = json.loads(row['properties'])
        if query.lower() in row['name'].lower() or any(query.lower() in str(value).lower() for value in properties.values()):
            results.append({'name': row['name'], **properties})

    return jsonify({'results': results}), 200

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            properties TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)