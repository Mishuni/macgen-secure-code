import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re

# Initialize SQLite database
def init_db():
    db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Validate product name and data
def validate_product(name, data):
    if not isinstance(name, str) or not name.strip():
        return False
    if not isinstance(data, dict):
        return False
    # Additional validation for data can be added here
    return True

# Add a new product to the catalog
async def add_product(request):
    try:
        product = await request.json()
        name = product['name']
        data = product  # Store the entire product as JSON

        if not validate_product(name, data):
            return web.Response(status=400)

        db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, json.dumps(data)))
        conn.commit()
        conn.close()

        return web.Response(status=201)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400)
    except sqlite3.IntegrityError:
        return web.Response(status=409)  # Conflict if product already exists
    except Exception as e:
        return web.Response(status=500)  # Internal server error

# Download the entire current catalog for a given product name
async def download_product(request):
    name = request.query.get('name')
    if not name or not isinstance(name, str) or not name.strip():
        return web.Response(status=400)

    db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return web.json_response(json.loads(row[0]))
    else:
        return web.Response(status=404)

# Upload data for a product
async def upload_product(request):
    try:
        product = await request.json()
        name = product['name']
        data = product['data']

        if not validate_product(name, data):
            return web.Response(status=400)

        db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (json.dumps(data), name))
        if cursor.rowcount == 0:
            return web.Response(status=404)
        conn.commit()
        conn.close()

        return web.Response(status=200)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400)
    except Exception as e:
        return web.Response(status=500)  # Internal server error

# Search for products in the catalog
async def search_products(request):
    query = request.query.get('query')
    if not query or not isinstance(query, str) or not query.strip():
        return web.json_response({'results': []})

    db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products')
    rows = cursor.fetchall()
    conn.close()

    results = []
    for name, data in rows:
        product = json.loads(data)
        if re.search(re.escape(query.lower()), name.lower()) or any(re.search(re.escape(query.lower()), str(value).lower()) for value in product.values()):
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