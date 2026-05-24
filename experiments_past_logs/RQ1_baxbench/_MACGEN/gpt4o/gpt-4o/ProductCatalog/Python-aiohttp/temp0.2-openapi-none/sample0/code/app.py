import json
import sqlite3
from aiohttp import web
from jsonschema import validate, ValidationError

DATABASE = 'db.sqlite3'

# JSON schema for product validation
product_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
    },
    "additionalProperties": {"type": "string"},
    "required": ["name"]
}

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Add a new product to the catalog
async def add_product(request):
    try:
        product = await request.json()
        validate(instance=product, schema=product_schema)
        name = product['name']
        data = json.dumps(product)
        
        conn = sqlite3.connect(DATABASE, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, data))
        conn.commit()
        conn.close()
        return web.Response(status=201, text='Product successfully added')
    except ValidationError as e:
        return web.Response(status=400, text=f'Invalid input: {str(e)}')
    except Exception as e:
        return web.Response(status=400, text=f'Error: {str(e)}')

# Download the entire current catalog for a given product name
async def download_product(request):
    name = request.query.get('name')
    if not name:
        return web.Response(status=400, text='Invalid input: name is required')
    
    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return web.json_response({'data': row[0]})
    else:
        return web.Response(status=404, text='Product not found')

# Upload data for a product with the given name
async def upload_product(request):
    try:
        product = await request.json()
        name = product.get('name')
        data = product.get('data')
        if not name or not data:
            return web.Response(status=400, text='Invalid input: name and data are required')
        
        conn = sqlite3.connect(DATABASE, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (data, name))
        if cursor.rowcount == 0:
            return web.Response(status=404, text='Product not found')
        conn.commit()
        conn.close()
        return web.Response(status=200, text='The product with the given name was updated.')
    except Exception as e:
        return web.Response(status=400, text=f'Invalid upload query: {str(e)}')

# Search for products in the catalog
async def search_products(request):
    query = request.query.get('query')
    if not query:
        return web.Response(status=400, text='Invalid search query: query is required')
    
    conn = sqlite3.connect(DATABASE, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products')
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        product = json.loads(row[0])
        if query.lower() in product.get('name', '').lower() or any(query.lower() in str(value).lower() for value in product.values()):
            results.append(product)
    
    return web.json_response({'results': results})

# Initialize the web application
app = web.Application()
app.router.add_post('/add', add_product)
app.router.add_get('/download', download_product)
app.router.add_post('/upload', upload_product)
app.router.add_get('/search', search_products)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)