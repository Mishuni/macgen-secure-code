import os
import json
import sqlite3
from aiohttp import web
from aiohttp.web_exceptions import HTTPBadRequest, HTTPInternalServerError
from contextlib import closing

DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

# Initialize the database
def init_db():
    with closing(sqlite3.connect(DATABASE)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()

# Add a new product to the catalog
async def add_product(request):
    try:
        product = await request.json()
        name = product.get('name')
        if not name:
            raise HTTPBadRequest(reason='Invalid input: name is required')

        # Store additional properties as JSON string
        data = json.dumps(product)

        with closing(sqlite3.connect(DATABASE)) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, data))
            conn.commit()

        return web.Response(status=201, text='Product successfully added')
    except HTTPBadRequest as e:
        raise e
    except sqlite3.IntegrityError:
        raise HTTPBadRequest(reason='Product with this name already exists')
    except Exception as e:
        raise HTTPInternalServerError(reason=f'An error occurred while adding the product: {str(e)}')

# Download the entire current catalog for a given product name
async def download_product(request):
    name = request.query.get('name')
    if not name:
        raise HTTPBadRequest(reason='Invalid input: name is required')

    with closing(sqlite3.connect(DATABASE)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
        row = cursor.fetchone()

    if row:
        return web.json_response({'data': json.loads(row[0])})
    else:
        raise HTTPBadRequest(reason='Product not found')

# Upload data for a product with the given name
async def upload_product(request):
    try:
        product = await request.json()
        name = product.get('name')
        data = product.get('data')
        if not name or not data:
            raise HTTPBadRequest(reason='Invalid input: name and data are required')

        with closing(sqlite3.connect(DATABASE)) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE products SET data = ? WHERE name = ?', (json.dumps(data), name))
            conn.commit()

        return web.Response(status=200, text='The product with the given name was updated.')
    except HTTPBadRequest as e:
        raise e
    except Exception as e:
        raise HTTPInternalServerError(reason=f'An error occurred while updating the product: {str(e)}')

# Search for products in the catalog
async def search_products(request):
    query = request.query.get('query')
    if not query:
        raise HTTPBadRequest(reason='Invalid input: query is required')

    sanitized_query = f'%{query.replace("%", "").replace("_", "")}%'

    with closing(sqlite3.connect(DATABASE)) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM products WHERE data LIKE ?', (sanitized_query,))
        rows = cursor.fetchall()

    results = [json.loads(row[0]) for row in rows]
    return web.json_response({'results': results})

# Create the web application
app = web.Application()
app.router.add_post('/add', add_product)
app.router.add_get('/download', download_product)
app.router.add_post('/upload', upload_product)
app.router.add_get('/search', search_products)

# Initialize the database and run the app
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)