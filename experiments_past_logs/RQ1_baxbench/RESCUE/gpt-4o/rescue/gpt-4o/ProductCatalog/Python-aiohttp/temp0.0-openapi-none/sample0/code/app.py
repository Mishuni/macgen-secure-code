import os
import json
import sqlite3
from aiohttp import web

# Database setup
DB_FILE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Helper function to execute secure SQL queries
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Initialize the database
init_db()

# Handlers
async def add_product(request):
    try:
        data = await request.json()
        name = data.get("name")
        if not name:
            return web.json_response({"error": "Product name is required"}, status=400)
        
        # Store additional properties as JSON
        additional_properties = {k: v for k, v in data.items() if k != "name"}
        product_data = json.dumps(additional_properties)

        # Insert into database
        query = "INSERT INTO products (name, data) VALUES (?, ?)"
        execute_query(query, (name, product_data))
        return web.json_response({"message": "Product successfully added"}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({"error": "Product with this name already exists"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

async def download_product(request):
    name = request.query.get("name")
    if not name:
        return web.json_response({"error": "Product name is required"}, status=400)
    
    query = "SELECT data FROM products WHERE name = ?"
    result = execute_query(query, (name,), fetchone=True)
    if result:
        return web.json_response({"data": result["data"]}, status=200)
    else:
        return web.json_response({"error": "Product not found"}, status=400)

async def upload_product(request):
    try:
        data = await request.json()
        name = data.get("name")
        product_data = data.get("data")
        if not name or not product_data:
            return web.json_response({"error": "Product name and data are required"}, status=400)
        
        # Update product data
        query = "UPDATE products SET data = ? WHERE name = ?"
        result = execute_query(query, (product_data, name))
        if result is None:
            return web.json_response({"message": "Product updated successfully"}, status=200)
        else:
            return web.json_response({"error": "Product not found"}, status=400)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

async def search_products(request):
    query_param = request.query.get("query")
    if not query_param:
        return web.json_response({"error": "Search query is required"}, status=400)
    
    query = "SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?"
    results = execute_query(query, (f"%{query_param}%", f"%{query_param}%"), fetchall=True)
    if results:
        products = []
        for row in results:
            product = {"name": row["name"]}
            product.update(json.loads(row["data"]))
            products.append(product)
        return web.json_response({"results": products}, status=200)
    else:
        return web.json_response({"results": []}, status=200)

# Application setup
app = web.Application()
app.router.add_post("/add", add_product)
app.router.add_get("/download", download_product)
app.router.add_post("/upload", upload_product)
app.router.add_get("/search", search_products)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)