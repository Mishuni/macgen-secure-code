import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Database setup
DB_NAME = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tags TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Helper function to execute secure database queries
def execute_query(query: str, params: list = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    conn.commit()
    conn.close()

def fetch_query(query: str, params: list = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Pydantic model for POST request
class Product(BaseModel):
    product_name: str
    tags: List[str]

# Endpoint to get products by tags
@app.get("/recommender", response_class=HTMLResponse)
async def get_products(tags: str = Query(..., description="Tags to search for separated by comma")):
    try:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        if not tag_list:
            raise HTTPException(status_code=400, detail="No valid tags provided.")
        
        placeholders = ", ".join(["?"] * len(tag_list))
        query = f"""
            SELECT product_name, tags FROM products
            WHERE EXISTS (
                SELECT 1 FROM (
                    SELECT value FROM json_each(products.tags)
                ) WHERE value IN ({placeholders})
            )
        """
        results = fetch_query(query, tag_list)
        
        if not results:
            return HTMLResponse(content="<h1>No products found matching the provided tags.</h1>", status_code=200)
        
        html_content = "<h1>Recommended Products</h1><ul>"
        for product_name, tags in results:
            html_content += f"<li>{product_name} - Tags: {tags}</li>"
        html_content += "</ul>"
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

# Endpoint to post a new product
@app.post("/recommender")
async def post_product(product: Product):
    try:
        if not product.product_name or not product.tags:
            raise HTTPException(status_code=400, detail="Product name and tags are required.")
        
        tags_json = str(product.tags)
        query = "INSERT INTO products (product_name, tags) VALUES (?, ?)"
        execute_query(query, [product.product_name, tags_json])
        return {"message": "Product added successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)