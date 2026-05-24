from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)

# Database setup
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

@app.route('/recommender', methods=['GET', 'POST'])
def recommender():
    if request.method == 'GET':
        tags = request.args.get('tags')
        if not tags:
            return "Tags are required", 400
        
        tag_list = tags.split(',')
        tag_list = [tag.strip() for tag in tag_list]
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            query = "SELECT product_name, tags FROM products WHERE "
            query += " OR ".join("tags LIKE ?" for _ in tag_list)
            cursor.execute(query, [f'%{tag}%' for tag in tag_list])
            products = cursor.fetchall()
        
        if products:
            html_content = "<h1>Recommended Products</h1><ul>"
            for product_name, tags in products:
                html_content += f"<li>{product_name} - Tags: {tags}</li>"
            html_content += "</ul>"
            return render_template_string(html_content)
        else:
            return "<h1>No products found</h1>", 200

    elif request.method == 'POST':
        data = request.get_json()
        product_name = data.get('product_name')
        tags = data.get('tags')

        if not product_name or not isinstance(tags, list):
            return "Invalid input", 400
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", 
                           (product_name, ','.join(tags)))
            conn.commit()
        
        return "Product added successfully", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)