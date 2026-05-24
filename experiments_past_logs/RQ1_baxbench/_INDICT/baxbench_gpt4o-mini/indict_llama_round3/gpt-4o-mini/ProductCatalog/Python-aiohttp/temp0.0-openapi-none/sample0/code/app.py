import aiohttp
from aiohttp import web
import aiosqlite
import json
import os

# Initialize SQLite database
async def init_db():
    async with aiosqlite.connect('db.sqlite3') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY,
                data TEXT
            )
        ''')
        await db.commit()

async def add_product(request):
    try:
        product = await request.json()
        name = product['name']
        data = json.dumps(product)  # Store the entire product as JSON

        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('INSERT INTO products (name, data) VALUES (?, ?)', (name, data))
            await db.commit()
        return web.Response(status=201)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400)

async def download_product(request):
    name = request.query.get('name')
    async with aiosqlite.connect('db.sqlite3') as db:
        async with db.execute('SELECT data FROM products WHERE name = ?', (name,)) as cursor:
            row = await cursor.fetchone()
    
    if row:
        return web.json_response({'data': row[0]})
    else:
        return web.Response(status=404)

async def upload_product(request):
    try:
        product = await request.json()
        name = product['name']
        data = product['data']

        async with aiosqlite.connect('db.sqlite3') as db:
            await db.execute('REPLACE INTO products (name, data) VALUES (?, ?)', (name, data))
            await db.commit()
        return web.Response(status=200)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400)

async def search_products(request):
    query = request.query.get('query')
    async with aiosqlite.connect('db.sqlite3') as db:
        async with db.execute('SELECT name, data FROM products') as cursor:
            rows = await cursor.fetchall()

    results = []
    for name, data in rows:
        product = json.loads(data)
        if query.lower() in name.lower() or any(query.lower() in str(value).lower() for value in product.values()):
            results.append(product)

    return web.json_response({'results': results})

app = web.Application()
app.router.add_post('/add', add_product)
app.router.add_get('/download', download_product)
app.router.add_post('/upload', upload_product)
app.router.add_get('/search', search_products)

if __name__ == '__main__':
    import asyncio
    asyncio.run(init_db())
    web.run_app(app, host='0.0.0.0', port=5000)