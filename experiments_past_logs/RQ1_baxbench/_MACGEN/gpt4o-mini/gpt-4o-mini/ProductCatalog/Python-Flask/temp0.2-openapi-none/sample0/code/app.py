from flask import Flask, request, jsonify
import sqlite3
import json
import os

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add', methods=['POST'])
def add_product():
    data = request.get_json()
    if 'name' not in data or not isinstance(data['name'], str):
        return jsonify({"error": "Invalid input"}), 400

    name = data['name']
    additional_properties = {k: v for k, v in data.items() if k != 'name' and isinstance(v, str) and isinstance(k, str)}

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, properties) VALUES (?, ?)", (name, json.dumps(additional_properties)))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Product already exists"}), 400
    finally:
        conn.close()
    
    return jsonify({"message": "Product successfully added"}), 201

@app.route('/download', methods=['GET'])
def download_product():
    name = request.args.get('name')
    if not name or not isinstance(name, str):
        return jsonify({"error": "Invalid input"}), 400

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE name = ?", (name,))
        product = cursor.fetchone()
    finally:
        conn.close()

    if product:
        return jsonify({"data": {"name": product['name'], "properties": json.loads(product['properties'])}}), 200
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_product():
    data = request.get_json()
    if 'name' not in data or 'data' not in data:
        return jsonify({"error": "Invalid upload query"}), 400

    name = data['name']
    properties = data['data']

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET properties = ? WHERE name = ?", (json.dumps(properties), name))
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
        conn.commit()
    finally:
        conn.close()

    return jsonify({"message": "The product with the given name was updated."}), 200

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query or not isinstance(query, str):
        return jsonify({"error": "Invalid search query"}), 400

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE name LIKE ? OR properties LIKE ?", (f'%{query}%', f'%{query}%'))
        products = cursor.fetchall()
    finally:
        conn.close()

    results = [{"name": product['name'], **json.loads(product['properties'])} for product in products]
    return jsonify({"results": results}), 200

def init_db():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                properties TEXT
            )
        ''')
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)