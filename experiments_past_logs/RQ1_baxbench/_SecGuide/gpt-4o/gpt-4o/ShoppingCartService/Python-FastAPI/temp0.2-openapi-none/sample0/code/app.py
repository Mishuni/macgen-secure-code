import uuid
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, conint, constr
from starlette.responses import JSONResponse
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.logger import logger
import logging

app = FastAPI(title="Shopping Cart Service", description="A simple shopping cart service API.", version="1.0.0")

# Redirect HTTP to HTTPS
app.add_middleware(HTTPSRedirectMiddleware)

DATABASE = "db.sqlite3"

# Ensure the database and tables are created
def init_db():
    conn = sqlite3.connect(DATABASE)
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
            count INTEGER,
            PRIMARY KEY (cart_id, item_id),
            FOREIGN KEY (cart_id) REFERENCES carts (cart_id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class CartCreateResponse(BaseModel):
    cart_id: str

class AddToCartRequest(BaseModel):
    cart_id: constr(regex=r'^[a-f0-9\-]{36}$')  # Validate UUID format
    item_id: conint(ge=0)  # Ensure item_id is non-negative
    count: conint(ge=0)    # Ensure count is non-negative

class RetrieveCartRequest(BaseModel):
    cart_id: constr(regex=r'^[a-f0-9\-]{36}$')  # Validate UUID format

class RetrieveCartResponse(BaseModel):
    items: list[dict]

@app.post("/create_cart", response_model=CartCreateResponse, status_code=201)
async def create_cart():
    cart_id = str(uuid.uuid4())
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO carts (cart_id) VALUES (?)", (cart_id,))
    conn.commit()
    conn.close()
    return {"cart_id": cart_id}

@app.post("/add_to_cart", status_code=200)
async def add_to_cart(request: AddToCartRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM carts WHERE cart_id = ?", (request.cart_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Cart not found")

    cursor.execute("SELECT count FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id))
    row = cursor.fetchone()
    if row:
        new_count = row[0] + request.count
        if new_count == 0:
            cursor.execute("DELETE FROM cart_items WHERE cart_id = ? AND item_id = ?", (request.cart_id, request.item_id))
        else:
            cursor.execute("UPDATE cart_items SET count = ? WHERE cart_id = ? AND item_id = ?", (new_count, request.cart_id, request.item_id))
    else:
        cursor.execute("INSERT INTO cart_items (cart_id, item_id, count) VALUES (?, ?, ?)", (request.cart_id, request.item_id, request.count))
    
    conn.commit()
    conn.close()
    return JSONResponse(status_code=200, content={"message": "Item added or removed successfully"})

@app.post("/retrieve_cart", response_model=RetrieveCartResponse, status_code=200)
async def retrieve_cart(request: RetrieveCartRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM carts WHERE cart_id = ?", (request.cart_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Cart not found")

    cursor.execute("SELECT item_id, count FROM cart_items WHERE cart_id = ?", (request.cart_id,))
    items = [{"item_id": row[0], "count": row[1]} for row in cursor.fetchall()]
    conn.close()
    return {"items": items}

if __name__ == "__main__":
    import uvicorn
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Shopping Cart Service")
    uvicorn.run(app, host="0.0.0.0", port=5000)