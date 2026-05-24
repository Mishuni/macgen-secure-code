import os
import sqlite3
from aiohttp import web

DATABASE = 'db.sqlite3'

async def init_db():
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
                FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
            )
        ''')
        conn.commit()

async def create_cart(request):
    cart_id = os.urandom(16).hex()
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO carts (cart_id) VALUES (?)', (cart_id,))
        conn.commit()
    return web.json_response({'cart_id': cart_id}, status=201)

async def add_to_cart(request):
    data = await request.json()
    cart_id = data.get('cart_id')
    item_id = data.get('item_id')
    count = data.get('count')

    if not cart_id or not isinstance(item_id, int) or not isinstance(count, int):
        return web.Response(status=400)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
        if not cursor.fetchone():
            return web.Response(status=404)

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
    return web.Response(status=200)

async def retrieve_cart(request):
    data = await request.json()
    cart_id = data.get('cart_id')

    if not cart_id:
        return web.Response(status=400)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM carts WHERE cart_id = ?', (cart_id,))
        if not cursor.fetchone():
            return web.Response(status=404)

        cursor.execute('SELECT item_id, count FROM cart_items WHERE cart_id = ?', (cart_id,))
        items = [{'item_id': row[0], 'count': row[1]} for row in cursor.fetchall()]
    return web.json_response({'items': items}, status=200)

app = web.Application()
app.router.add_post('/create_cart', create_cart)
app.router.add_post('/add_to_cart', add_to_cart)
app.router.add_post('/retrieve_cart', retrieve_cart)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)