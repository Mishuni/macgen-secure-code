import os
import sqlite3
from flask import Flask, request, jsonify, abort
from flask.sessions import SecureCookieSessionInterface

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.environ.get('APP_SECRET', 'default_secret')

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
            CREATE TABLE IF NOT EXISTS carts (
                cart_id TEXT PRIMARY KEY
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER,
                PRIMARY KEY (cart_id, item_id),
                FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
            )
        ''')
        db.commit()

@app.route('/create_cart', methods=['POST'])
def create_cart():
    db = get_db()
    cursor = db.cursor()
    cart_id = os.urandom(16).hex()
    cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    db.commit()
    return jsonify({'cart_id': cart_id}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or not item_id or count is None:
        abort(400, description="Invalid request")

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
    cart = cursor.fetchone()

    if not cart:
        abort(404, description="Cart not found")

    cursor.execute('SELECT * FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
    item = cursor.fetchone()

    if item:
        new_count = item['count'] + count
        if new_count <= 0:
            cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        else:
            cursor.execute('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
    else:
        if count > 0:
            cursor.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

    db.commit()
    return jsonify({'message': 'Item added or removed successfully'}), 200

@app.route('/retrieve_cart', methods=['POST'])
def retrieve_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')

    if not cart_id:
        abort(400, description="Invalid request")

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
    cart = cursor.fetchone()

    if not cart:
        abort(404, description="Cart not found")

    cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
    items = cursor.fetchall()
    items_list = [{'item_id': item['item_id'], 'count': item['count']} for item in items]

    return jsonify({'items': items_list}), 200

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)