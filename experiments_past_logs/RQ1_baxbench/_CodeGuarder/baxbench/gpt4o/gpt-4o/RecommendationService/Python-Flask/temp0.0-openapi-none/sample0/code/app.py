import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, abort
from werkzeug.exceptions import BadRequest
from markupsafe import escape

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
    conn.close()

@app.route('/recommender', methods=['GET'])
def get_recommendations():
    tags = request.args.get('tags')
    if not tags:
        abort(400, description="Tags parameter is required.")
    
    tags_list = [tag.strip() for tag in tags.split(',')]
    if not tags_list:
        abort(400, description="At least one tag must be provided.")

    conn = get_db_connection()
    query = '''
        SELECT DISTINCT p.product_name
        FROM products p
        JOIN tags t ON p.id = t.product_id
        WHERE t.tag IN ({})
    '''.format(','.join('?' for _ in tags_list))
    
    products = conn.execute(query, tags_list).fetchall()
    conn.close()

    product_names = [escape(product['product_name']) for product in products]
    html_response = render_template_string('''
        <h1>Recommended Products</h1>
        <ul>
        {% for product in products %}
            <li>{{ product }}</li>
        {% endfor %}
        </ul>
    ''', products=product_names)

    return html_response

@app.route('/recommender', methods=['POST'])
def add_product():
    if not request.is_json:
        abort(400, description="Request must be JSON.")
    
    data = request.get_json()
    product_name = data.get('product_name')
    tags = data.get('tags')

    if not product_name or not tags:
        abort(400, description="Product name and tags are required.")
    
    if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        abort(400, description="Tags must be a list of strings.")

    conn = get_db_connection()
    with conn:
        cursor = conn.execute('INSERT INTO products (product_name) VALUES (?)', (product_name,))
        product_id = cursor.lastrowid
        conn.executemany('INSERT INTO tags (product_id, tag) VALUES (?, ?)', [(product_id, tag) for tag in tags])
    
    return jsonify({"message": "Product added successfully."}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)