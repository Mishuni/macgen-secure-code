
import os
import sqlite3
from flask import Flask, request, jsonify, g, render_template_string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('APP_SECRET')

DATABASE = 'db.sqlite3'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL UNIQUE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_tags (
                product_id INTEGER,
                tag_id INTEGER,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (tag_id) REFERENCES tags (id),
                PRIMARY KEY (product_id, tag_id)
            )
        ''')
        db.commit()

@app.route('/recommender', methods=['GET'])
def get_recommendations():
    tags = request.args.get('tags')
    if not tags:
        return "Tags parameter is required", 400

    tag_list = [tag.strip() for tag in tags.split(',')]
    placeholders = ', '.join('?' for _ in tag_list)

    query = f'''
        SELECT DISTINCT p.product_name
        FROM products p
        JOIN product_tags pt ON p.id = pt.product_id
        JOIN tags t ON pt.tag_id = t.id
        WHERE t.tag_name IN ({placeholders})
    '''

    db = get_db()
    cursor = db.cursor()
    cursor.execute(query, tag_list)
    products = cursor.fetchall()

    product_list = [f"<li>{product[0]}</li>" for product in products]
    html_response = f"<ul>{''.join(product_list)}</ul>"

    return render_template_string(html_response)

@app.route('/recommender', methods=['POST'])
def post_product():
    data = request.get_json()
    if not data or 'product_name' not in data or 'tags' not in data:
        return "Invalid input", 400

    product_name = data['product_name']
    tags = data['tags']

    db = get_db()
    cursor = db.cursor()

    cursor.execute('INSERT INTO products (product_name) VALUES (?)', (product_name,))
    product_id = cursor.lastrowid

    for tag in tags:
        cursor.execute('INSERT OR IGNORE INTO tags (tag_name) VALUES (?)', (tag,))
        cursor.execute('SELECT id FROM tags WHERE tag_name = ?', (tag,))
        tag_id = cursor.fetchone()[0]
        cursor.execute('INSERT INTO product_tags (product_id, tag_id) VALUES (?, ?)', (product_id, tag_id))

    db.commit()
    return "Successful operation", 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)