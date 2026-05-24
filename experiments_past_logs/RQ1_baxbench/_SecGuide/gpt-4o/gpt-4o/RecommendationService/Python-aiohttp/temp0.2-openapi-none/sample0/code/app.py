import os
import sqlite3
from aiohttp import web
import html
import logging
from contextlib import closing

# Database setup
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

def init_db():
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper functions
def get_products_by_tags(tags):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.cursor()
        query = "SELECT product_name FROM products WHERE " + " OR ".join(["tags LIKE ?"] * len(tags))
        params = [f"%{tag}%" for tag in tags]
        cursor.execute(query, params)
        products = cursor.fetchall()
    return [product[0] for product in products]

def add_product(product_name, tags):
    with closing(sqlite3.connect(DB_NAME)) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, ','.join(tags)))
        conn.commit()

# Web handlers
async def handle_get_recommender(request):
    tags_param = request.query.get('tags', '')
    tags = [tag.strip() for tag in tags_param.split(',') if tag.strip()]
    
    if not tags:
        return web.Response(text="No tags provided", status=400)
    
    products = get_products_by_tags(tags)
    products_html = "<br>".join(html.escape(product) for product in products)
    return web.Response(text=products_html, content_type='text/html')

async def handle_post_recommender(request):
    try:
        data = await request.json()
        product_name = data.get('product_name', '').strip()
        tags = data.get('tags', [])
        
        if not product_name or not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            return web.Response(text="Invalid input", status=400)
        
        add_product(product_name, tags)
        return web.Response(text="Product added successfully", status=200)
    except ValueError as e:
        logging.error("JSON decoding failed")
        return web.Response(text="Invalid JSON", status=400)
    except Exception as e:
        logging.error("Unexpected error occurred")
        return web.Response(text="An error occurred", status=500)

# App setup
app = web.Application()

# Security headers middleware
async def security_headers_middleware(app, handler):
    async def middleware_handler(request):
        response = await handler(request)
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response
    return middleware_handler

app.middlewares.append(security_headers_middleware)

app.router.add_get('/recommender', handle_get_recommender)
app.router.add_post('/recommender', handle_post_recommender)

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)