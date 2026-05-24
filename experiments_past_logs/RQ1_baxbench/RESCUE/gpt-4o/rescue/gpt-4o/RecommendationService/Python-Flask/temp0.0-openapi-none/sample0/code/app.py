import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET", "default_secret")

# Database initialization
DATABASE = "db.sqlite3"

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
        """)
        conn.commit()

init_db()

# Helper function to execute queries securely
def execute_query(query, args=(), fetch=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        if fetch:
            return cursor.fetchall()
        conn.commit()

@app.route('/recommender', methods=['GET'])
def get_recommendations():
    tags = request.args.get('tags')
    if not tags:
        return "Tags parameter is required.", 400

    # Split tags and prepare for SQL query
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if not tag_list:
        return "No valid tags provided.", 400

    # Use parameterized query to prevent SQL injection
    placeholders = ', '.join(['?'] * len(tag_list))
    query = f"""
    SELECT product_name, tags FROM products
    WHERE EXISTS (
        SELECT 1 FROM (SELECT ? AS tag UNION ALL SELECT ? AS tag) AS input_tags
        WHERE ',' || products.tags || ',' LIKE '%,' || input_tags.tag || ',%'
    )
    """
    results = execute_query(query, tag_list, fetch=True)

    # Render results as HTML
    html_template = """
    <!DOCTYPE html>
    <html>
    <head><title>Product Recommendations</title></head>
    <body>
        <h1>Recommended Products</h1>
        <ul>
        {% for product, tags in results %}
            <li><strong>{{ product }}</strong> (Tags: {{ tags }})</li>
        {% end %}
    </body>
    </html>
    """
    return render_template_string(html_template, results=results)

@app.route('/recommender', methods=['POST'])
def post_product():
    data = request.json
    if not data or 'product_name' not in data or 'tags' not in data:
        return jsonify({"error": "Invalid input"}), 400

    product_name = data['product_name']
    tags = data['tags']

    if not isinstance(product_name, str) or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        return jsonify({"error": "Invalid input"}), 400

    # Join tags into a comma-separated string
    tags_str = ','.join(tag.strip() for tag in tags if tag.strip())
    if not tags_str:
        return jsonify({"error": "No valid tags provided"}), 400

    # Use parameterized query to prevent SQL injection
    query = "INSERT INTO products (product_name, tags) VALUES (?, ?)"
    execute_query(query, (product_name, tags_str))

    return jsonify({"message": "Product added successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)