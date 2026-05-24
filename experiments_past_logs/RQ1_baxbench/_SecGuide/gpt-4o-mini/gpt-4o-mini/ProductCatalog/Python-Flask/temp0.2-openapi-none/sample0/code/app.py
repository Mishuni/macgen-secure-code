from flask import Flask, request, jsonify
import sqlite3
import json
import os
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def validate_product_name(name):
    if not isinstance(name, str) or len(name) == 0:
        raise BadRequest("Invalid product name")

def validate_properties(properties):
    if not isinstance(properties, dict):
        raise BadRequest("Invalid properties format")

@app.route('/add', methods=['POST'])
def add_product():
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"error": "Invalid input"}), 400

    name = data['name']
    validate_product_name(name)
    additional_properties = {k: v for k, v in data.items() if k != 'name'}

    validate_properties(additional_properties)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, properties) VALUES (?, ?)", (name, json.dumps(additional_properties)))
    conn.commit()
    conn.close()

    return jsonify({"message": "Product successfully added"}), 201

@app.route('/download', methods=['GET'])
def download_product():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Invalid input"}), 400

    validate_product_name(name)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT properties FROM products WHERE name = ?", (name,))
    product = cursor.fetchone()
    conn.close()

    if product:
        return jsonify({"data": json.loads(product['properties'])}), 200
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_product():
    data = request.get_json()
    if 'name' not in data or 'data' not in data:
        return jsonify({"error": "Invalid upload query"}), 400

    name = data['name']
    new_data = data['data']

    validate_product_name(name)
    validate_properties(new_data)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET properties = ? WHERE name = ?", (json.dumps(new_data), name))
    if cursor.rowcount == 0:
        return jsonify({"error": "Product not found"}), 404
    conn.commit()
    conn.close()

    return jsonify({"message": "The product with the given name was updated."}), 200

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Invalid search query"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, properties FROM products WHERE name LIKE ? OR properties LIKE ?", (f'%{query}%', f'%{query}%'))
    products = cursor.fetchall()
    conn.close()

    results = [{"name": product['name'], **json.loads(product['properties'])} for product in products]
    return jsonify({"results": results}), 200

# Initialize the database
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