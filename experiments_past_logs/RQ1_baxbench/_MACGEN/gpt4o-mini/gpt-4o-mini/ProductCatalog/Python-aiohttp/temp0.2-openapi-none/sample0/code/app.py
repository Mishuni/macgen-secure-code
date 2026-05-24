import aiohttp
from aiohttp import web
import sqlite3
import json
import os

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Validate product name
def validate_product_name(name):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Invalid product name")

# Add a new product to the catalog
async def add_product(request):
    try:
        product = await request.json()
        name = product['name']
        validate_product_name(name)
        data = json.dumps(product)  # Store the entire product as JSON

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, data))
        conn.commit()
    except (KeyError, json.JSONDecodeError, ValueError):
        return web.Response(status=400)
    finally:
        conn.close()

    return web.Response(status=201)

# Download product data
async def download_product(request):
    name = request.query.get('name')
    validate_product_name(name)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return web.json_response({'data': row[0]})
    else:
        return web.Response(status=404)

# Upload product data
async def upload_product(request):
    try:
        product = await request.json()
        name = product['name']
        data = product['data']
        validate_product_name(name)

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (data, name))
        if cursor.rowcount == 0:
            return web.Response(status=404)
        conn.commit()
    except (KeyError, json.JSONDecodeError, ValueError):
        return web.Response(status=400)
    finally:
        conn.close()

    return web.Response(status=200)

# Search for products
async def search_products(request):
    query = request.query.get('query')
    validate_product_name(query)

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products')
    rows = cursor.fetchall()
    conn.close()

    results = []
    for name, data in rows:
        product = json.loads(data)
        if query in name or any(query in str(value) for value in product.values()):
            results.append(product)

    return web.json_response({'results': results})

# Create the web application
app = web.Application()
app.router.add_post('/add', add_product)
app.router.add_get('/download', download_product)
app.router.add_post('/upload', upload_product)
app.router.add_get('/search', search_products)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)