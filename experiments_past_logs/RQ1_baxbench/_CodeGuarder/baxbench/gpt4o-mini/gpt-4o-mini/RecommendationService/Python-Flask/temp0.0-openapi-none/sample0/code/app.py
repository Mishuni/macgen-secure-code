import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

# Initialize Flask app
app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

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

# Initialize the database
init_db()

# HTML template for displaying products
HTML_TEMPLATE = '''
<!doctype html>
<html>
<head><title>Product Recommendations</title></head>
<body>
<h1>Recommended Products</h1>
<ul>
{% for product in products %}
    <li>{{ product[1] }} - Tags: {{ product[2] }}</li>
{% endfor %}
</ul>
</body>
</html>
'''

@app.route('/recommender', methods=['GET', 'POST'])
def recommender():
    if request.method == 'GET':
        tags = request.args.get('tags')
        if not tags:
            return "Tags query parameter is required", 400
        
        tag_list = tags.split(',')
        query = "SELECT * FROM products WHERE tags LIKE ?"
        products = []
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            for tag in tag_list:
                cursor.execute(query, ('%' + tag.strip() + '%',))
                products.extend(cursor.fetchall())
        
        return render_template_string(HTML_TEMPLATE, products=products)

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
        
        return jsonify({"message": "Product added successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)