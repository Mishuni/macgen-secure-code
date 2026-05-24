from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
from markupsafe import escape

app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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

def sanitize_tags(tags):
    # Normalize and validate tags
    allowed_tags = set(['electronics', 'furniture', 'clothing', 'toys', 'books'])  # Example allow list
    sanitized = [tag.strip() for tag in tags.split(',') if tag.strip() in allowed_tags]
    return sanitized

@app.route('/recommender', methods=['GET', 'POST'])
def recommender():
    if request.method == 'GET':
        tags = request.args.get('tags')
        if not tags:
            return 'Tags are required', 400
        
        sanitized_tags = sanitize_tags(tags)
        if not sanitized_tags:
            return 'No valid tags provided', 400
        
        tag_placeholders = ' OR '.join(['tags LIKE ?'] * len(sanitized_tags))
        query_params = ['%' + tag + '%' for tag in sanitized_tags]
        
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT product_name, tags FROM products
            WHERE {tag_placeholders}
        ''', query_params)
        
        products = cursor.fetchall()
        conn.close()
        
        html_content = '<h1>Recommended Products</h1><ul>'
        for product_name, tags in products:
            html_content += f'<li>{escape(product_name)} - Tags: {escape(tags)}</li>'
        html_content += '</ul>'
        
        return render_template_string(html_content)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'product_name' not in data or 'tags' not in data:
            return 'Invalid input', 400
        
        product_name = data['product_name']
        tags = ','.join(sanitize_tags(data['tags']))
        
        if not tags:
            return 'No valid tags provided', 400
        
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, tags))
        conn.commit()
        conn.close()
        
        return 'Product added successfully', 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)