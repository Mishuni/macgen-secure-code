import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn

app = FastAPI()

# Database setup
DATABASE_FILE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Models
class Product(BaseModel):
    name: str
    data: Optional[Dict[str, str]] = None

class ProductUpload(BaseModel):
    name: str
    data: str

# Endpoints
@app.post("/add", status_code=201)
async def add_product(product: Product):
    if not product.name:
        raise HTTPException(status_code=400, detail="Product name is required")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (product.name, str(product.data)))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    finally:
        conn.close()
    return {"message": "Product successfully added"}

@app.get("/download")
async def download_product(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"data": row["data"]}
    else:
        raise HTTPException(status_code=404, detail="Product not found")

@app.post("/upload", status_code=200)
async def upload_product(product: ProductUpload):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET data = ? WHERE name = ?', (product.data, product.name))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=400, detail="Product not found")
    conn.commit()
    conn.close()
    return {"message": "Product successfully updated"}

@app.get("/search")
async def search_products(query: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()
    results = [{"name": row["name"], **eval(row["data"])} for row in rows]
    return {"results": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)