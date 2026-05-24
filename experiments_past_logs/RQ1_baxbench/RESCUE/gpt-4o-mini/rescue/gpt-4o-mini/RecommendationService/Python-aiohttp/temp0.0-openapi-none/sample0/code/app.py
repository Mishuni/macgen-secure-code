import aiohttp
from aiohttp import web
import sqlite3
import os

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
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

# Get products by tags
async def get_products(request):
    tags = request.query.get('tags')
    if not tags:
        return web.Response(status=400, text="Tags parameter is required.")

    tag_list = tags.split(',')
    placeholders = ', '.join('?' for _ in tag_list)
    sql = f"SELECT product_name FROM products WHERE tags LIKE '%' || ? || '%' OR tags LIKE '%' || ? || '%'" * len(tag_list)
    
    # Prepare the arguments for the query
    args = [tag for tag in tag_list for _ in (0, 1)]  # Duplicate each tag for the LIKE clause

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute(sql, args)
    products = cursor.fetchall()
    conn.close()

    # Format the response as HTML
    product_list = ''.join(f"<li>{product[0]}</li>" for product in products)
    response_html = f"<ul>{product_list}</ul>"
    return web.Response(text=response_html, content_type='text/html')

# Post a new product
async def post_product(request):
    try:
        data = await request.json()
        product_name = data['product_name']
        tags = ','.join(data['tags'])

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", (product_name, tags))
        conn.commit()
        conn.close()

        return web.Response(status=200, text="Product added successfully.")
    except (KeyError, ValueError):
        return web.Response(status=400, text="Invalid input.")

# Create the web application
app = web.Application()
app.router.add_get('/recommender', get_products)
app.router.add_post('/recommender', post_product)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)