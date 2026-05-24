import os
import sqlite3
from aiohttp import web
import json

# Initialize the database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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

# Create a new shopping cart
async def create_cart(request):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cart_id = os.urandom(16).hex()
    cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
    conn.commit()
    conn.close()
    return web.json_response({'cart_id': cart_id}, status=201)

# Add or remove items from the cart
async def add_to_cart(request):
    try:
        data = await request.json()
        cart_id = data.get('cart_id')
        item_id = data.get('item_id')
        count = data.get('count')

        if not cart_id or not isinstance(item_id, int) or not isinstance(count, int):
            return web.Response(text='Invalid request', status=400)

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
        if not cursor.fetchone():
            conn.close()
            return web.Response(text='Cart not found', status=404)

        cursor.execute('SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        row = cursor.fetchone()
        if row:
            new_count = row[0] + count
            if new_count <= 0:
                cursor.execute('DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
            else:
                cursor.execute('UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
        else:
            if count > 0:
                cursor.execute('INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

        conn.commit()
        conn.close()
        return web.Response(text='Item added or removed successfully', status=200)
    except json.JSONDecodeError:
        return web.Response(text='Invalid JSON', status=400)

# Retrieve all items in the cart
async def retrieve_cart(request):
    try:
        data = await request.json()
        cart_id = data.get('cart_id')

        if not cart_id:
            return web.Response(text='Invalid request', status=400)

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
        if not cursor.fetchone():
            conn.close()
            return web.Response(text='Cart not found', status=404)

        cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
        items = [{'item_id': row[0], 'count': row[1]} for row in cursor.fetchall()]
        conn.close()
        return web.json_response({'items': items}, status=200)
    except json.JSONDecodeError:
        return web.Response(text='Invalid JSON', status=400)

# Setup the application and routes
app = web.Application()
app.router.add_post('/create_cart', create_cart)
app.router.add_post('/add_to_cart', add_to_cart)
app.router.add_post('/retrieve_cart', retrieve_cart)

# Initialize the database and run the app
init_db()
web.run_app(app, host='0.0.0.0', port=5000)