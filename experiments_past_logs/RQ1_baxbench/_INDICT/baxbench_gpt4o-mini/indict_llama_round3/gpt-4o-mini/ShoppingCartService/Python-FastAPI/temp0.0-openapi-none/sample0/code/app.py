from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, conint
import sqlite3
import os

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS carts (
                cart_id TEXT PRIMARY KEY
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cart_items (
                cart_id TEXT,
                item_id INTEGER,
                count INTEGER CHECK(count >= 0),
                PRIMARY KEY (cart_id, item_id),
                FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
            )
        ''')
        conn.commit()

init_db()

class CreateCartResponse(BaseModel):
    cart_id: str

class AddToCartRequest(BaseModel):
    cart_id: str
    item_id: int
    count: conint(ge=-100)  # Allow negative counts for removal

class RetrieveCartRequest(BaseModel):
    cart_id: str

class CartItem(BaseModel):
    item_id: int
    count: int

class RetrieveCartResponse(BaseModel):
    items: list[CartItem]

@app.post("/create_cart", response_model=CreateCartResponse, status_code=201)
def create_cart():
    cart_id = os.urandom(16).hex()  # Generate a random cart ID
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO carts (cart_id) VALUES (?)", (cart_id,))
        conn.commit()
    return CreateCartResponse(cart_id=cart_id)

@app.post("/add_to_cart", status_code=200)
def add_to_cart(request: AddToCartRequest):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carts WHERE cart_id = ?", (request.cart_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Cart not found")

        if request.count < 0:
            cursor.execute("""
                UPDATE cart_items SET count = count + ?
                WHERE cart_id = ? AND item_id = ?
            """, (request.count, request.cart_id, request.item_id))
            cursor.execute("""
                DELETE FROM cart_items WHERE cart_id = ? AND item_id = ? AND count <= 0
            """, (request.cart_id, request.item_id))
        else:
            cursor.execute("""
                INSERT INTO cart_items (cart_id, item_id, count)
                VALUES (?, ?, ?)
                ON CONFLICT(cart_id, item_id) DO UPDATE SET count = count + ?
            """, (request.cart_id, request.item_id, request.count, request.count))
        conn.commit()

@app.post("/retrieve_cart", response_model=RetrieveCartResponse)
def retrieve_cart(request: RetrieveCartRequest):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM carts WHERE cart_id = ?", (request.cart_id,))
        if cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Cart not found")

        cursor.execute("SELECT item_id, count FROM cart_items WHERE cart_id = ?", (request.cart_id,))
        items = [CartItem(item_id=row[0], count=row[1]) for row in cursor.fetchall()]
        return RetrieveCartResponse(items=items)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)