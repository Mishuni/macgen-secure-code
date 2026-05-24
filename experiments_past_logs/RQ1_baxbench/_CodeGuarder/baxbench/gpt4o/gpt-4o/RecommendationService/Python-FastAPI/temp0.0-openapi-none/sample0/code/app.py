import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
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

init_db()

# Pydantic models
class Product(BaseModel):
    product_name: str
    tags: List[str]

# GET endpoint
@app.get("/recommender", response_class=HTMLResponse)
async def get_products(tags: str = Query(..., description="Tags to search for separated by comma")):
    tag_list = [tag.strip() for tag in tags.split(',')]
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE " + " OR ".join(["tags LIKE ?"] * len(tag_list))
    params = [f"%{tag}%" for tag in tag_list]
    cursor.execute(query, params)
    products = cursor.fetchall()
    conn.close()

    if not products:
        return HTMLResponse(content="<h1>No products found</h1>", status_code=200)

    html_content = "<h1>Recommended Products</h1><ul>"
    for product in products:
        html_content += f"<li>{product['product_name']} - Tags: {product['tags']}</li>"
    html_content += "</ul>"
    return HTMLResponse(content=html_content, status_code=200)

# POST endpoint
@app.post("/recommender")
async def post_product(product: Product):
    if not product.product_name or not product.tags:
        raise HTTPException(status_code=400, detail="Invalid input")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (product_name, tags) VALUES (?, ?)",
        (product.product_name, ','.join(product.tags))
    )
    conn.commit()
    conn.close()
    return {"message": "Product added successfully"}

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)