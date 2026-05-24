import os
import sqlite3
from flask import Flask, request, jsonify, g

# Flask app initialization
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Database file
DATABASE = 'db.sqlite3'

# Helper function to get database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# Close database connection when app context ends
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize database
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL
            )
        ''')
        db.commit()

# Route to add a new product
@app.route('/add', methods=['POST'])
def add_product():
    try:
        json_data = request.get_json()
        if not json_data or 'name' not in json_data:
            return jsonify({"error": "Invalid input"}), 400

        name = json_data['name']
        data = {k: v for k, v in json_data.items() if k != 'name'}

        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, str(data)))
        db.commit()

        return jsonify({"message": "Product successfully added"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Product with this name already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to download product data
@app.route('/download', methods=['GET'])
def download_product():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Product name is required"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
        row = cursor.fetchone()

        if row:
            return jsonify({"data": row['data']}), 200
        else:
            return jsonify({"error": "Product not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to upload product data
@app.route('/upload', methods=['POST'])
def upload_product():
    try:
        json_data = request.get_json()
        if not json_data or 'name' not in json_data or 'data' not in json_data:
            return jsonify({"error": "Invalid input"}), 400

        name = json_data['name']
        data = json_data['data']

        db = get_db()
        cursor = db.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (data, name))
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 400
        db.commit()

        return jsonify({"message": "Product successfully updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to search for products
@app.route('/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('query')
        if not query:
            return jsonify({"error": "Search query is required"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()

        results = []
        for row in rows:
            product = {"name": row['name']}
            product.update(eval(row['data']))
            results.append(product)

        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Main entry point
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)