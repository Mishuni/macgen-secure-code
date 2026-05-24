import aiohttp
from aiohttp import web
import sqlite3
import uuid
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
            FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
        )
    ''')
    conn.commit()
    conn.close()

# Input validation functions
def validate_item_id(item_id):
    return isinstance(item_id, int) and item_id > 0

def validate_count(count):
    return isinstance(count, int) and count >= 0

def validate_cart_id(cart_id):
    # Simple UUID validation
    return re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', cart_id) is not None

# API Handlers
async def create_cart(request):
    cart_id = str(uuid.uuid4())  # Generate a unique cart ID using UUID
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    conn.commit()
    conn.close()
    return web.json_response({'cart_id': cart_id}, status=201)

async def add_to_cart(request):
    data = await request.json()
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not all([cart_id, item_id, count is not None]) or not validate_cart_id(cart_id) or not validate_item_id(item_id) or not validate_count(count):
        return web.json_response({'error': 'Invalid request'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM carts WHERE cart_id = ?', (cart_id,))
    if cursor.fetchone() is None:
        conn.close()
        return web.json_response({'error': 'Invalid cart ID'}, status=404)

    if count == 0:
        cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
    else:
        cursor.execute('INSERT OR REPLACE INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

    conn.commit()
    conn.close()
    return web.json_response({'message': 'Item added or removed successfully'}, status=200)

async def retrieve_cart(request):
    data = await request.json()
    cart_id = data.get('cart_id')

    if not cart_id or not validate_cart_id(cart_id):
        return web.json_response({'error': 'Invalid request'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
    items = cursor.fetchall()
    conn.close()

    return web.json_response({'items': [{'item_id': item[0], 'count': item[1]} for item in items]}, status=200)

# App setup
app = web.Application()
app.router.add_post('/create_cart', create_cart)
app.router.add_post('/add_to_cart', add_to_cart)
app.router.add_post('/retrieve_cart', retrieve_cart)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)