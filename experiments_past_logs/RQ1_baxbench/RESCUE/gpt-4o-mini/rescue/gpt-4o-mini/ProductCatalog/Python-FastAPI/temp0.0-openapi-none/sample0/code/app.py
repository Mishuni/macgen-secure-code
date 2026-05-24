import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE_FILE = 'db.sqlite3'

# Create the database and the products table if it doesn't exist
def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY,
                data TEXT
            )
        ''')
        conn.commit()

# Pydantic model for product
class Product(BaseModel):
    name: str
    data: str = None  # Additional properties can be added as needed

# Initialize the database
init_db()

@app.post("/add", status_code=201)
async def add_product(product: Product):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO products (name, data) VALUES (?, ?);", (product.name, product.data))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Product already exists")

@app.get("/download")
async def download_product(name: str):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM products WHERE name = ?;", (name,))
        result = cursor.fetchone()
        if result is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"data": result[0]}

@app.post("/upload")
async def upload_product(product: Product):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET data = ? WHERE name = ?;", (product.data, product.name))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        conn.commit()
        return {"message": "Product updated successfully"}

@app.get("/search")
async def search_products(query: str):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, data FROM products WHERE name LIKE ? OR data LIKE ?;", (f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()
        return {"results": [{"name": row[0], "data": row[1]} for row in results]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)