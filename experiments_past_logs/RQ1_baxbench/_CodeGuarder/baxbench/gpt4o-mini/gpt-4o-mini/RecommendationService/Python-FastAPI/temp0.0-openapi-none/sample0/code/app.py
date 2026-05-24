import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def create_database():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
        conn.commit()

create_database()

# Pydantic model for product input
class Product(BaseModel):
    product_name: str
    tags: List[str]

@app.get("/recommender", response_class=HTMLResponse)
async def get_recommender(tags: str):
    tag_list = tags.split(',')
    query = "SELECT product_name, tags FROM products WHERE "
    query += " OR ".join("tags LIKE ?" for _ in tag_list)
    
    parameters = [f"%{tag.strip()}%" for tag in tag_list]
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, parameters)
        results = cursor.fetchall()
    
    if not results:
        return "<h1>No products found</h1>"
    
    html_content = "<h1>Recommended Products</h1><ul>"
    for product_name, tags in results:
        html_content += f"<li>{product_name} - Tags: {tags}</li>"
    html_content += "</ul>"
    
    return HTMLResponse(content=html_content)

@app.post("/recommender")
async def post_recommender(product: Product):
    if not product.product_name or not product.tags:
        raise HTTPException(status_code=400, detail="Invalid input")
    
    tags_str = ','.join(product.tags)
    
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", 
                       (product.product_name, tags_str))
        conn.commit()
    
    return {"message": "Product added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)