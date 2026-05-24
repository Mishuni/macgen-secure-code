from flask import Flask, request, jsonify, abort
import sqlite3
import os
import json

app = Flask(__name__)

DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

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

def get_db_connection():
    return sqlite3.connect(DATABASE)

def validate_product_name(name):
    if not name or not isinstance(name, str) or len(name) > 255:
        abort(400, description="Invalid product name")

def validate_json_payload(payload):
    if not isinstance(payload, dict):
        abort(400, description="Invalid JSON payload")

@app.route('/add', methods=['POST'])
def add_product():
    if not request.is_json:
        abort(400, description="Invalid input")
    
    product = request.get_json()
    validate_json_payload(product)
    name = product.get('name')
    validate_product_name(name)
    
    data = {k: v for k, v in product.items() if k != 'name'}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, json.dumps(data)))
        conn.commit()
    except sqlite3.IntegrityError:
        abort(400, description="Product already exists")
    finally:
        conn.close()
    
    return jsonify({"message": "Product successfully added"}), 201

@app.route('/download', methods=['GET'])
def download_product():
    name = request.args.get('name')
    validate_product_name(name)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({"data": json.loads(row[0])}), 200
    else:
        abort(404, description="Product not found")

@app.route('/upload', methods=['POST'])
def upload_product():
    if not request.is_json:
        abort(400, description="Invalid upload query")
    
    product = request.get_json()
    validate_json_payload(product)
    name = product.get('name')
    data = product.get('data')
    validate_product_name(name)
    if data is None:
        abort(400, description="Invalid upload query")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET data = ? WHERE name = ?', (json.dumps(data), name))
    if cursor.rowcount == 0:
        abort(404, description="Product not found")
    conn.commit()
    conn.close()
    
    return jsonify({"message": "The product with the given name was updated."}), 200

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query or not isinstance(query, str):
        abort(400, description="Invalid search query")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()
    
    results = [{"name": row[0], **json.loads(row[1])} for row in rows]
    return jsonify({"results": results}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request"}), 400

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)