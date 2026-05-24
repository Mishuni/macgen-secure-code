from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
from typing import List

app = FastAPI(
    title="Recommendation",
    description="Product recommendation service to provide a list of posted products searched by tag.",
    version="1.0.11"
)

DATABASE = "db.sqlite3"

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
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

class Product(BaseModel):
    product_name: str
    tags: List[str]

@app.get("/recommender", response_class=HTMLResponse, summary="Get all posted products that match at least one of the provided tags.")
async def get_recommendations(tags: str = Query(..., description="Tags to search for separated by comma.")):
    tag_list = [tag.strip() for tag in tags.split(',')]
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    query = "SELECT product_name, tags FROM products"
    cursor.execute(query)
    products = cursor.fetchall()
    conn.close()

    matching_products = []
    for product_name, product_tags in products:
        product_tags_set = set(tag.strip() for tag in product_tags.split(','))
        if product_tags_set.intersection(tag_list):
            matching_products.append(product_name)

    if not matching_products:
        return HTMLResponse(content="<p>No products found matching the given tags.</p>", status_code=200)

    html_content = "<ul>"
    for product in matching_products:
        html_content += f"<li>{product}</li>"
    html_content += "</ul>"

    return HTMLResponse(content=html_content, status_code=200)

@app.post("/recommender", summary="Post a new product along with its tags.")
async def post_product(product: Product):
    if not product.product_name or not product.tags:
        raise HTTPException(status_code=400, detail="Invalid input")

    tags_str = ','.join(tag.strip() for tag in product.tags)
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (product_name, tags) VALUES (?, ?)", (product.product_name, tags_str))
    conn.commit()
    conn.close()

    return {"message": "Product added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)