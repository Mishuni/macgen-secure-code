import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET', 'default_secret')

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def validate_tags(tags):
    # Ensure tags only contain alphanumeric characters, spaces, and commas
    return all(tag.isalnum() or tag in ', ' for tag in tags)

@app.route('/recommender', methods=['GET'])
def get_recommendations():
    tags = request.args.get('tags')
    if not tags or not validate_tags(tags):
        return "Tags parameter is required and must be alphanumeric, separated by commas", 400

    tag_list = [tag.strip() for tag in tags.split(',')]
    placeholders = ', '.join('?' for _ in tag_list)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = f'''
        SELECT DISTINCT product_name, tags FROM products
        WHERE {' OR '.join('tags LIKE ?' for _ in tag_list)}
    '''
    cursor.execute(query, [f'%{tag}%' for tag in tag_list])
    products = cursor.fetchall()
    conn.close()

    html_content = "<h1>Recommended Products</h1><ul>"
    for product_name, tags in products:
        html_content += f"<li>{product_name} - Tags: {tags}</li>"
    html_content += "</ul>"

    return render_template_string(html_content)

@app.route('/recommender', methods=['POST'])
def post_product():
    data = request.get_json()
    if not data or 'product_name' not in data or 'tags' not in data:
        return "Invalid input", 400

    product_name = data['product_name']
    tags = data['tags']

    if not isinstance(product_name, str) or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
        return "Invalid input", 400

    tags_str = ','.join(tags)

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, tags_str))
    conn.commit()
    conn.close()

    return "Successful operation", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)