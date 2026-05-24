import os
import sqlite3
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')  # Use a secure, consistent secret key

DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/recommender', methods=['GET'])
def get_recommendations():
    tags = request.args.get('tags')
    if not tags:
        return "Tags parameter is required", 400

    tags_list = [tag.strip() for tag in tags.split(',')]
    if not all(tags_list):
        return "Invalid tags input", 400

    placeholders = ','.join(['?'] * len(tags_list))
    query = f"SELECT product_name FROM products WHERE tags LIKE '%' || ? || '%'"

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, tags_list)
            products = cursor.fetchall()
    except sqlite3.Error:
        return jsonify({"error": "Database error occurred"}), 500

    product_list = [product[0] for product in products]
    return render_template('recommendations.html', products=product_list)

@app.route('/recommender', methods=['POST'])
def post_product():
    if not request.is_json:
        return jsonify({"error": "Invalid input"}), 400

    data = request.get_json()
    product_name = data.get('product_name')
    tags = data.get('tags')

    if not product_name or not tags or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        return jsonify({"error": "Invalid input"}), 400

    if len(product_name) > 255 or any(len(tag) > 255 for tag in tags):
        return jsonify({"error": "Input size too large"}), 400

    tags_str = ','.join(tags)

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, tags_str))
            conn.commit()
    except sqlite3.Error:
        return jsonify({"error": "Database error occurred"}), 500

    return jsonify({"message": "Product added successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)