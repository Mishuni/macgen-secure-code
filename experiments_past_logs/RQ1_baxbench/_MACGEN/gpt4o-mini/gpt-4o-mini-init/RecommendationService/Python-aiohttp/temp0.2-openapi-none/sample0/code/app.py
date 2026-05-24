import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re

DB_NAME = 'db.sqlite3'

# Initialize the SQLite database
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

# Function to validate tags
def validate_tags(tags):
    if not all(re.match("^[a-zA-Z0-9_]+$", tag) for tag in tags):
        raise ValueError("Invalid tag format")

# Function to add a new product to the database
def add_product(product_name, tags):
    validate_tags(tags)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', (product_name, ','.join(tags)))
    conn.commit()
    conn.close()

# Function to retrieve products based on tags
def get_products_by_tags(tags):
    validate_tags(tags)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    products = []
    for tag in tags:
        cursor.execute('SELECT product_name, tags FROM products WHERE tags LIKE ?', ('%' + tag + '%',))
        products.extend(cursor.fetchall())
    conn.close()
    return products

# Aiohttp request handlers
async def handle_get(request):
    tags = request.query.get('tags')
    if not tags:
        return web.Response(status=400, text='Tags are required')

    tags_list = tags.split(',')
    products = get_products_by_tags(tags_list)
    response_html = '<h1>Recommended Products</h1><ul>'
    for product_name, tags in products:
        response_html += f'<li>{product_name} - Tags: {tags}</li>'
    response_html += '</ul>'
    return web.Response(text=response_html, content_type='text/html')

async def handle_post(request):
    try:
        data = await request.json()
        product_name = data['product_name']
        tags = data['tags']
        if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
            return web.Response(status=400, text='Invalid input')
        add_product(product_name, tags)
        return web.Response(status=200)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid input')

# Main function to run the web server
def main():
    init_db()
    app = web.Application()
    app.router.add_get('/recommender', handle_get)
    app.router.add_post('/recommender', handle_post)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()