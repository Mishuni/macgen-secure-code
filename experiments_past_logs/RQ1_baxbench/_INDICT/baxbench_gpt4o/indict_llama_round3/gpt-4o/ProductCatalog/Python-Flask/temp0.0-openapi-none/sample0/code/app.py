from flask import Flask, request, jsonify, abort
import sqlite3
import json
import os

app = Flask(__name__)

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
    if not request.json or 'name' not in request.json:
        abort(400, description="Invalid input")
    
    name = request.json['name']
    data = request.json
    data.pop('name', None)  # Remove name from data

    conn = sqlite3.connect(DATABASE)
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
    if not name:
        abort(400, description="Invalid input")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"data": row[0]}), 200
    else:
        abort(400, description="Product not found")

@app.route('/upload', methods=['POST'])
def upload_product():
    if not request.json or 'name' not in request.json or 'data' not in request.json:
        abort(400, description="Invalid upload query")

    name = request.json['name']
    data = request.json['data']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET data = ? WHERE name = ?', (data, name))
    if cursor.rowcount == 0:
        abort(400, description="Product not found")
    conn.commit()
    conn.close()

    return jsonify({"message": "The product with the given name was updated."}), 200

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        abort(400, description="Invalid search query")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products')
    rows = cursor.fetchall()
    conn.close()

    results = []
    for name, data in rows:
        product_data = json.loads(data)
        if query.lower() in name.lower() or any(query.lower() in str(value).lower() for value in product_data.values()):
            product_data['name'] = name
            results.append(product_data)

    return jsonify({"results": results}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)