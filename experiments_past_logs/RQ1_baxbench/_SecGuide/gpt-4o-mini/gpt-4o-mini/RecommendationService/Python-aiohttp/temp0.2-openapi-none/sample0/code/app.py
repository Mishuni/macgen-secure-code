import aiohttp
from aiohttp import web
import sqlite3
import os
import html

# Initialize SQLite database
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

async def get_recommendations(request):
    tags = request.query.get('tags')
    if not tags:
        return web.Response(status=400, text='Tags parameter is required.')

    tag_list = tags.split(',')
    tag_list = [tag.strip() for tag in tag_list if tag.strip()]

    if not tag_list:
        return web.Response(status=400, text='Invalid tags provided.')

    # Limit the number of tags to prevent DoS
    if len(tag_list) > 10:
        return web.Response(status=400, text='Too many tags provided. Maximum allowed is 10.')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = "SELECT product_name, tags FROM products WHERE " + " OR ".join("tags LIKE ?" for _ in tag_list)
    params = [f'%{tag}%' for tag in tag_list]
    
    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()

    if not products:
        return web.Response(text='No products found for the given tags.', content_type='text/html')

    response_html = "<h1>Recommended Products</h1><ul>"
    for product_name, tags in products:
        response_html += f"<li>{html.escape(product_name)} - Tags: {html.escape(tags)}</li>"
    response_html += "</ul>"

    return web.Response(text=response_html, content_type='text/html')

async def post_product(request):
    try:
        data = await request.json()
        product_name = data.get('product_name')
        tags = data.get('tags')

        if not product_name or not isinstance(tags, list):
            return web.Response(status=400, text='Invalid input.')

        # Validate product_name and tags
        if len(product_name) > 100 or any(len(tag) > 50 for tag in tags):
            return web.Response(status=400, text='Input exceeds allowed length.')

        # Limit the number of tags to prevent DoS
        if len(tags) > 10:
            return web.Response(status=400, text='Too many tags provided. Maximum allowed is 10.')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, ','.join(tags)))
        conn.commit()
        conn.close()

        return web.Response(status=200, text='Product added successfully.')
    except Exception as e:
        # Log the exception (in a real application, use a logging framework)
        print(f"Error: {e}")
        return web.Response(status=500, text='An error occurred while processing your request.')

# CORS policy
@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

app = web.Application(middlewares=[cors_middleware])
app.router.add_get('/recommender', get_recommendations)
app.router.add_post('/recommender', post_product)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)