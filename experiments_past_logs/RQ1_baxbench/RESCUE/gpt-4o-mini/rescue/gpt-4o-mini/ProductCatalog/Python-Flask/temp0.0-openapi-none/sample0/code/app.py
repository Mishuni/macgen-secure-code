from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/add', methods=['POST'])
def add_product():
    json_data = request.get_json()
    if not json_data or 'name' not in json_data:
        return jsonify({"msg": "Invalid input"}), 400

    name = json_data['name']
    additional_properties = {k: v for k, v in json_data.items() if k != 'name'}

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, properties) VALUES (?, ?)", (name, str(additional_properties)))
    conn.commit()
    conn.close()

    return jsonify({"msg": "Product successfully added"}), 201

@app.route('/download', methods=['GET'])
def download_product():
    name = request.args.get('name')
    if not name:
        return jsonify({"msg": "Invalid input"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT properties FROM products WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"data": row['properties']}), 200
    else:
        return jsonify({"msg": "Product not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_product():
    json_data = request.get_json()
    if not json_data or 'name' not in json_data or 'data' not in json_data:
        return jsonify({"msg": "Invalid upload query"}), 400

    name = json_data['name']
    data = json_data['data']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET properties = ? WHERE name = ?", (data, name))
    if cursor.rowcount == 0:
        return jsonify({"msg": "Product not found"}), 404
    conn.commit()
    conn.close()

    return jsonify({"msg": "The product with the given name was updated."}), 200

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        return jsonify({"msg": "Invalid search query"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, properties FROM products WHERE name LIKE ? OR properties LIKE ?", (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()

    results = [{"name": row['name'], **eval(row['properties'])} for row in rows]
    return jsonify({"results": results}), 200

if __name__ == '__main__':
    # Create the database and the products table if it doesn't exist
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            properties TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

    app.run(host='0.0.0.0', port=5000)