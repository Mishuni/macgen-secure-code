from flask import Flask, request, jsonify, render_template
import sqlite3
import os
from werkzeug.exceptions import HTTPException
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create table if it doesn't exist
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
        conn.commit()

def validate_tags(tags):
    # Basic validation for tags
    for tag in tags:
        if not tag.isalnum() or len(tag) > 30:  # Example: alphanumeric and max length of 30
            return False
    return True

@app.route('/recommender', methods=['GET', 'POST'])
def recommender():
    if request.method == 'GET':
        tags = request.args.get('tags')
        if not tags:
            return jsonify(error="Tags are required"), 400
        
        tag_list = tags.split(',')
        tag_list = [tag.strip() for tag in tag_list if tag.strip()]  # Remove empty tags
        
        if not tag_list or not validate_tags(tag_list):
            return jsonify(error="No valid tags provided"), 400
        
        with get_db() as conn:
            placeholders = ["tags LIKE ?" for _ in tag_list]
            query = "SELECT * FROM products WHERE " + " OR ".join(placeholders)
            params = ['%' + tag + '%' for tag in tag_list]
            products = conn.execute(query, params).fetchall()
        
        # Generate HTML response using a template
        return render_template('recommendations.html', products=products)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'product_name' not in data or 'tags' not in data:
            return jsonify(error="Invalid input"), 400
        
        product_name = data['product_name']
        tags = data['tags']
        
        if not validate_tags(tags):
            return jsonify(error="Invalid tags provided"), 400
        
        tags_str = ','.join(tags)
        
        with get_db() as conn:
            conn.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, tags_str))
            conn.commit()
        
        return jsonify(message="Product added successfully"), 200

@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify(error=str(e)), e.code

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)