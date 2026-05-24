from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint, constr
import sqlite3
import os
import uuid
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
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

class CreateCartResponse(BaseModel):
    cart_id: str

class AddToCartRequest(BaseModel):
    cart_id: constr(regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')  # UUID format
    item_id: int
    count: conint(ge=0)  # count must be a non-negative integer

class RetrieveCartRequest(BaseModel):
    cart_id: constr(regex=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')  # UUID format

class CartItem(BaseModel):
    item_id: int
    count: int

class RetrieveCartResponse(BaseModel):
    items: list[CartItem]

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.post("/create_cart", response_model=CreateCartResponse, status_code=201)
def create_cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    cart_id = str(uuid.uuid4())  # Use UUID for cart_id
    cursor.execute("INSERT INTO carts (id) VALUES (?)", (cart_id,))
    conn.commit()
    conn.close()
    logging.info(f"Cart created with ID: {cart_id}")
    return CreateCartResponse(cart_id=cart_id)

@app.post("/add_to_cart", status_code=200)
def add_to_cart(request: AddToCartRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if cart exists
    cursor.execute("SELECT * FROM carts WHERE id = ?", (request.cart_id,))
    cart = cursor.fetchone()
    if cart is None:
        conn.close()
        logging.warning(f"Attempt to add to non-existent cart: {request.cart_id}")
        raise HTTPException(status_code=404, detail="Cart not found")

    # Update cart items
    cursor.execute("SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id))
    item = cursor.fetchone()
    
    if item:
        new_count = item['count'] + request.count
        if new_count <= 0:
            cursor.execute("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id))
            logging.info(f"Item {request.item_id} removed from cart {request.cart_id}")
        else:
            cursor.execute("UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?", (new_count, request.cart_id, request.item_id))
            logging.info(f"Item {request.item_id} updated in cart {request.cart_id} to count {new_count}")
    else:
        if request.count > 0:
            cursor.execute("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)", (request.cart_id, request.item_id, request.count))
            logging.info(f"Item {request.item_id} added to cart {request.cart_id} with count {request.count}")
    
    conn.commit()
    conn.close()

@app.post("/retrieve_cart", response_model=RetrieveCartResponse)
def retrieve_cart(request: RetrieveCartRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if cart exists
    cursor.execute("SELECT * FROM carts WHERE id = ?", (request.cart_id,))
    cart = cursor.fetchone()
    if cart is None:
        conn.close()
        logging.warning(f"Attempt to retrieve non-existent cart: {request.cart_id}")
        raise HTTPException(status_code=404, detail="Cart not found")

    cursor.execute("SELECT item_id, count FROM cart_items WHERE cart_id = ?", (request.cart_id,))
    items = cursor.fetchall()
    
    conn.close()
    return RetrieveCartResponse(items=[CartItem(item_id=item['item_id'], count=item['count']) for item in items])

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS carts (id TEXT PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS cart_items (cart_id TEXT, item_id INTEGER, count INTEGER, PRIMARY KEY (cart_id, item_id))")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)