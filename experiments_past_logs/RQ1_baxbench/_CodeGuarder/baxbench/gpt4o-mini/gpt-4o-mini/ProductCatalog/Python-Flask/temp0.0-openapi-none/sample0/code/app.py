from flask import Flask, request, jsonify, Response
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_first_request
def initialize_database():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                data TEXT
            )
        ''')
        conn.commit()

@app.route('/add', methods=['POST'])
def add_product():
    try:
        product = request.get_json()
        if not product or 'name' not in product:
            return jsonify({"error": "Invalid input"}), 400
        
        with get_db() as conn:
            conn.execute('INSERT INTO products (name, data) VALUES (?, ?)', 
                         (product['name'], str(product)))
            conn.commit()
        return jsonify({"message": "Product successfully added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/download', methods=['GET'])
def download_product():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Product name is required"}), 400

    with get_db() as conn:
        product = conn.execute('SELECT * FROM products WHERE name = ?', (name,)).fetchone()
        if product:
            return jsonify({"data": dict(product)}), 200
        else:
            return jsonify({"error": "Product not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_product():
    try:
        product = request.get_json()
        if not product or 'name' not in product or 'data' not in product:
            return jsonify({"error": "Invalid upload query"}), 400

        with get_db() as conn:
            conn.execute('UPDATE products SET data = ? WHERE name = ?', 
                         (product['data'], product['name']))
            conn.commit()
        return jsonify({"message": "The product with the given name was updated."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Invalid search query"}), 400

    with get_db() as conn:
        products = conn.execute('SELECT * FROM products WHERE name LIKE ?', ('%' + query + '%',)).fetchall()
        results = [dict(product) for product in products]
        return jsonify({"results": results}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)