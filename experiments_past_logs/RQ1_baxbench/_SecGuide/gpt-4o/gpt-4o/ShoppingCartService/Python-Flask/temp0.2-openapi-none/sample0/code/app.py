from flask import Flask, request, jsonify, abort
import sqlite3
import uuid

app = Flask(__name__)

DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
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
                FOREIGN KEY (cart_id) REFERENCES carts(cart_id)
            )
        ''')
        conn.commit()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/create_cart', methods=['POST'])
def create_cart():
    cart_id = str(uuid.uuid4())
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
        conn.commit()
    return jsonify({'cart_id': cart_id}), 201

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or not isinstance(item_id, int) or not isinstance(count, int) or count == 0:
        abort(400, description="Invalid request")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
        if cursor.fetchone() is None:
            abort(404, description="Cart not found")

        cursor.execute('SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        row = cursor.fetchone()
        if row:
            new_count = row['count'] + count
            if new_count <= 0:
                cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
            else:
                cursor.execute('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
        else:
            if count > 0:
                cursor.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))
        conn.commit()
    return jsonify({'message': 'Item added or removed successfully'}), 200

@app.route('/retrieve_cart', methods=['GET'])
def retrieve_cart():
    cart_id = request.args.get('cart_id')

    if not cart_id:
        abort(400, description="Invalid request")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
        if cursor.fetchone() is None:
            abort(404, description="Cart not found")

        cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
        items = [{'item_id': row['item_id'], 'count': row['count']} for row in cursor.fetchall()]
    return jsonify({'items': items}), 200

@app.errorhandler(400)
@app.errorhandler(404)
def handle_error(error):
    response = jsonify({'error': 'An error occurred'})
    response.status_code = error.code
    return response

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)