from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Extra, constr
import sqlite3
import json
import os

app = FastAPI()

DATABASE = 'db.sqlite3'

class Product(BaseModel):
    name: str
    __root__: dict[str, str] = {}

    class Config:
        extra = Extra.allow

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/add", status_code=201)
def add_product(product: Product):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO products (name, data) VALUES (?, ?)', (product.name, json.dumps(product.__root__)))
        conn.commit()
    return {"message": "Product successfully added"}

@app.get("/download")
def download_product(name: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT data FROM products WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"data": row[0]}

@app.post("/upload")
def upload_product(product: Product):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE products SET data = ? WHERE name = ?', (json.dumps(product.__root__), product.name))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        conn.commit()
    return {"message": "The product with the given name was updated."}

@app.get("/search")
def search_products(query: str):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT name, data FROM products')
        rows = cursor.fetchall()
        results = []
        for row in rows:
            name, data = row
            if query in name or query in data:
                results.append({"name": name, **json.loads(data)})
        return {"results": results}