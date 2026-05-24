import os
import sqlite3
from flask import Flask, request, jsonify, abort, Response
from werkzeug.datastructures import Headers
from flask.sessions import SecureCookieSessionInterface

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.environ.get('APP_SECRET', 'default_secret_key')

DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        ''')
        db.commit()

@app.route('/add', methods=['POST'])
def add_product():
    if not request.is_json:
        abort(400, description="Invalid input")
    product = request.get_json()
    name = product.get('name')
    if not name:
        abort(400, description="Product name is required")
    data = {k: v for k, v in product.items() if k != 'name'}
    db = get_db()
    try:
        db.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, str(data)))
        db.commit()
    except sqlite3.IntegrityError:
        abort(400, description="Product already exists")
    return Response(status=201)

@app.route('/download', methods=['GET'])
def download_product():
    name = request.args.get('name')
    if not name:
        abort(400, description="Product name is required")
    db = get_db()
    cursor = db.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    if row is None:
        abort(400, description="Product not found")
    return jsonify(data=row['data'])

@app.route('/upload', methods=['POST'])
def upload_product():
    if not request.is_json:
        abort(400, description="Invalid upload query")
    product = request.get_json()
    name = product.get('name')
    data = product.get('data')
    if not name or not data:
        abort(400, description="Product name and data are required")
    db = get_db()
    db.execute('REPLACE INTO products (name, data) VALUES (?, ?)', (name, data))
    db.commit()
    return Response(status=200)

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        abort(400, description="Invalid search query")
    db = get_db()
    cursor = db.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
    results = [{'name': row['name'], **eval(row['data'])} for row in cursor.fetchall()]
    return jsonify(results=results)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)