from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Extra
import sqlite3
import os
from typing import Any, Dict, List

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

class Product(BaseModel):
    name: str
    __root__: Dict[str, Any] = {}

    class Config:
        extra = Extra.allow

@app.post("/add", status_code=201)
async def add_product(product: Product):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (product.name, str(product.__root__)))
            conn.commit()
            return {"message": "Product successfully added"}
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Product already exists")

@app.get("/download")
async def download_product(name: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            return {"data": row[0]}
        raise HTTPException(status_code=404, detail="Product not found")

@app.post("/upload")
async def upload_product(product: Product):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (str(product.__root__), product.name))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=400, detail="Product not found")
        conn.commit()
        return {"message": "Product successfully updated"}

@app.get("/search")
async def search_products(query: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, data FROM products')
        rows = cursor.fetchall()
        results = []
        for row in rows:
            name, data = row
            if query in name or query in data:
                # Safely convert the string representation of the dictionary back to a dictionary
                product_data = eval(data) if data else {}
                results.append({"name": name, **product_data})
        return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)