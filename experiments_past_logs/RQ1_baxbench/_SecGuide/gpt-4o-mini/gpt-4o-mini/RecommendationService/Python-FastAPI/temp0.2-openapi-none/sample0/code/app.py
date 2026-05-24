from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, constr, validator
import sqlite3
import os
from fastapi.middleware.cors import CORSMiddleware
import html

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for your application
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic model for product with input validation
class Product(BaseModel):
    product_name: constr(min_length=1, max_length=100)  # Validate product name length
    tags: list[constr(min_length=1, max_length=30)]  # Validate tag length

    @validator('tags', pre=True)
    def validate_tags(cls, tags):
        if not isinstance(tags, list):
            raise ValueError('Tags must be a list')
        return tags

@app.on_event("startup")
def startup():
    # Create table if it doesn't exist
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name TEXT NOT NULL,
                tags TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.get("/recommender", response_class=str)
async def recommend_products(tags: str = Query(..., description="Tags to search for separated by comma.")):
    tag_list = tags.split(',')
    tag_list = [tag.strip() for tag in tag_list if tag.strip()]  # Remove empty tags

    if not tag_list:
        return "<h1>No valid tags provided</h1>"

    with get_db_connection() as conn:
        query = "SELECT product_name, tags FROM products WHERE "
        query += " OR ".join("tags LIKE ?" for _ in tag_list)
        parameters = [f"%{tag}%" for tag in tag_list]
        
        products = conn.execute(query, parameters).fetchall()
    
    if not products:
        return "<h1>No products found</h1>"
    
    response_html = "<h1>Recommended Products</h1><ul>"
    for product in products:
        response_html += f"<li>{html.escape(product['product_name'])} - Tags: {html.escape(product['tags'])}</li>"
    response_html += "</ul>"
    
    return response_html

@app.post("/recommender")
async def post_product(product: Product):
    with get_db_connection() as conn:
        conn.execute('INSERT INTO products (product_name, tags) VALUES (?, ?)', 
                     (product.product_name, ','.join(product.tags)))
        conn.commit()
    return {"message": "Product added successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)