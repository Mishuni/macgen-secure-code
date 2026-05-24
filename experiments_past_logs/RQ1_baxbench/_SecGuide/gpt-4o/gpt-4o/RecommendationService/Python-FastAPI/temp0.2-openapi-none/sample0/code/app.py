import os
import sqlite3
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr, conlist
from typing import List
from contextlib import contextmanager
import logging

# Initialize FastAPI app
app = FastAPI(
    title="Recommendation",
    description="Product recommendation service to provide a list of posted products searched by tag.",
    version="1.0.11"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE = os.getenv("DATABASE_PATH", "db.sqlite3")

def init_db():
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

init_db()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# Pydantic model for product input
class Product(BaseModel):
    product_name: constr(min_length=1, strip_whitespace=True)
    tags: conlist(constr(min_length=1, strip_whitespace=True), min_items=1)

# Endpoint to get products by tags
@app.get("/recommender", response_class=JSONResponse)
async def get_products(tags: str = Query(..., description="Tags to search for separated by comma.")):
    tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    if not tag_list:
        raise HTTPException(status_code=400, detail="Invalid tags input")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT product_name, tags FROM products"
        cursor.execute(query)
        products = cursor.fetchall()

    matching_products = []
    for product_name, product_tags in products:
        product_tags_set = set(product_tags.split(","))
        if product_tags_set.intersection(tag_list):
            matching_products.append(product_name)

    if not matching_products:
        logger.info("No products found for tags: %s", tags)
        return JSONResponse(content={"message": "No products found"}, status_code=200)

    return JSONResponse(content={"matching_products": matching_products}, status_code=200)

# Endpoint to post a new product
@app.post("/recommender")
async def post_product(product: Product):
    tags_str = ",".join(product.tags)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", (product.product_name, tags_str))
            conn.commit()
        except sqlite3.Error as e:
            logger.error("Database error: %s", e)
            raise HTTPException(status_code=500, detail="Database error")

    return {"message": "Product added successfully"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)