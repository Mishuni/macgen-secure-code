import aiohttp
from aiohttp import web
import sqlite3
import uuid
import os
import json

DATABASE = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id TEXT PRIMARY KEY,
            item_id INTEGER,
            count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

async def create_cart(request):
    cart_id = str(uuid.uuid4())
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO cart (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, None, 0))
    conn.commit()
    conn.close()
    return web.json_response({'cart_id': cart_id}, status=201)

async def add_to_cart(request):
    try:
        data = await request.json()
        cart_id = data['cart_id']
        item_id = data['item_id']
        count = data['count']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cart WHERE cart_id = ?', (cart_id,))
        if cursor.fetchone() is None:
            return web.json_response({'error': 'Cart not found'}, status=404)

        cursor.execute('SELECT count FROM cart WHERE cart_id = ? AND item_id = ?', (cart_id, item_id))
        row = cursor.fetchone()
        if row:
            new_count = row[0] + count
            if new_count < 0:
                return web.json_response({'error': 'Count cannot be negative'}, status=400)
            cursor.execute('UPDATE cart SET count = ? WHERE cart_id = ? AND item_id = ?', (new_count, cart_id, item_id))
        else:
            if count < 0:
                return web.json_response({'error': 'Count cannot be negative'}, status=400)
            cursor.execute('INSERT INTO cart (cart_id, item_id, count) VALUES (?, ?, ?)', (cart_id, item_id, count))

        conn.commit()
        conn.close()
        return web.json_response({'message': 'Item added or removed successfully'}, status=200)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid request'}, status=400)

async def retrieve_cart(request):
    try:
        data = await request.json()
        cart_id = data['cart_id']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT item_id, count FROM cart WHERE cart_id = ?', (cart_id,))
        items = cursor.fetchall()
        conn.close()

        if not items:
            return web.json_response({'error': 'Cart not found'}, status=404)

        item_list = [{'item_id': item[0], 'count': item[1]} for item in items]
        return web.json_response({'items': item_list}, status=200)
    except (KeyError, json.JSONDecodeError):
        return web.json_response({'error': 'Invalid request'}, status=400)

app = web.Application()
app.router.add_post('/create_cart', create_cart)
app.router.add_post('/add_to_cart', add_to_cart)
app.router.add_post('/retrieve_cart', retrieve_cart)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)