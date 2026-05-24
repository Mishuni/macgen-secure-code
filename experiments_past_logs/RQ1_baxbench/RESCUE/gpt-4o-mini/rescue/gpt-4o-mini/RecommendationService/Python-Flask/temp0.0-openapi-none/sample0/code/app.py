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

@app.route('/recommender', methods=['GET'])
def recommend_products():
    tags = request.args.get('tags', default="")
    if not tags:
        return "Tags are required", 400

    tag_list = tags.split(',')
    placeholders = ', '.join('?' for _ in tag_list)
    sql = f"SELECT * FROM products WHERE tags IN ({placeholders})"
    
    with get_db() as conn:
        cursor = conn.execute(sql, tag_list)
        products = cursor.fetchall()

    # Generate HTML response
    html_response = "<h1>Recommended Products</h1><ul>"
    for product in products:
        html_response += f"<li>{product['product_name']} - Tags: {product['tags']}</li>"
    html_response += "</ul>"

    return html_response, 200

@app.route('/recommender', methods=['POST'])
def post_product():
    data = request.get_json()
    if not data or 'product_name' not in data or 'tags' not in data:
        return "Invalid input", 400

    product_name = data['product_name']
    tags = ','.join(data['tags'])

    sql = "INSERT INTO products (product_name, tags) VALUES (?, ?)"
    with get_db() as conn:
        conn.execute(sql, (product_name, tags))
        conn.commit()

    return "Product added successfully", 200

if __name__ == '__main__':
    # Create the database and table if they don't exist
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
    app.run(host='0.0.0.0', port=5000)