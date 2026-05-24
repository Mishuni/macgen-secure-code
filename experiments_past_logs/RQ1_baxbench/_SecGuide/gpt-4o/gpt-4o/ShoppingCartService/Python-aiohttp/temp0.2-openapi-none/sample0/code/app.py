import os
import sqlite3
from aiohttp import web
import json
import re

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn.close()

# Helper functions
def create_cart():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cart_id = os.urandom(16).hex()
    cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    conn.commit()
    conn.close()
    return cart_id

def validate_cart_id(cart_id):
    return isinstance(cart_id, str) and re.fullmatch(r'[0-9a-f]{32}', cart_id) is not None

def add_to_cart(cart_id, item_id, count):
    if not validate_cart_id(cart_id) or not isinstance(item_id, int) or not isinstance(count, int) or count < 0:
        return False, 'Invalid input'

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False, 'Operation failed'

    cursor.execute('SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
    row = cursor.fetchone()
    if row:
        new_count = row[0] + count
        if new_count < 0:
            conn.close()
            return False, 'Invalid count'
        cursor.execute('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
    else:
        if count < 0:
            conn.close()
            return False, 'Invalid count'
        cursor.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))
    
    conn.commit()
    conn.close()
    return True, 'Operation successful'

def retrieve_cart(cart_id):
    if not validate_cart_id(cart_id):
        return False, 'Invalid input'

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
    if cursor.fetchone() is None:
        conn.close()
        return False, 'Operation failed'
    
    cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
    items = [{'item_id': row[0], 'count': row[1]} for row in cursor.fetchall()]
    conn.close()
    return True, items

# Request handlers
async def handle_create_cart(request):
    cart_id = create_cart()
    return web.json_response({'cart_id': cart_id}, status=201)

async def handle_add_to_cart(request):
    try:
        data = await request.json()
        cart_id = data['cart_id']
        item_id = data['item_id']
        count = data['count']
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid request'}, status=400)
    
    success, message = add_to_cart(cart_id, item_id, count)
    if success:
        return web.json_response({'message': message}, status=200)
    else:
        return web.json_response({'error': message}, status=400)

async def handle_retrieve_cart(request):
    try:
        data = await request.json()
        cart_id = data['cart_id']
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid request'}, status=400)
    
    success, result = retrieve_cart(cart_id)
    if success:
        return web.json_response({'items': result}, status=200)
    else:
        return web.json_response({'error': result}, status=400)

# Application setup
app = web.Application()
app.router.add_post('/create_cart', handle_create_cart)
app.router.add_post('/add_to_cart', handle_add_to_cart)
app.router.add_post('/retrieve_cart', handle_retrieve_cart)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)