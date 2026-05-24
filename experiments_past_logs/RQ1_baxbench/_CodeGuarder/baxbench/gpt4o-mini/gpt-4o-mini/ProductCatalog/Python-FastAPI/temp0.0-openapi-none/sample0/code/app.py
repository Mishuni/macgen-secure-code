import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Extra
from typing import Any, Dict, List

# Load environment variables
APP_SECRET = os.getenv("APP_SECRET")

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic model for product
class Product(BaseModel):
    name: str
    __root__: Dict[str, Any] = {}

    class Config:
        extra = Extra.allow

# Create products table if it doesn't exist
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@app.post("/add", status_code=201)
async def add_product(product: Product):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO products (name, data) VALUES (?, ?)', (product.name, str(product.__root__)))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Product already exists")

@app.get("/download")
async def download_product(name: str):
    with get_db_connection() as conn:
        product = conn.execute('SELECT data FROM products WHERE name = ?', (name,)).fetchone()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"data": product["data"]}

@app.post("/upload")
async def upload_product(product: Product):
    with get_db_connection() as conn:
        conn.execute('UPDATE products SET data = ? WHERE name = ?', (str(product.__root__), product.name))
        conn.commit()
        return {"message": "Product updated"}

@app.get("/search")
async def search_products(query: str):
    with get_db_connection() as conn:
        products = conn.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%')).fetchall()
        return {"results": [{"name": row["name"], **eval(row["data"])} for row in products]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)