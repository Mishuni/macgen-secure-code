import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, EmailStr
import csv
from typing import List, Optional
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Pydantic models
class MerchantRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class MerchantLogin(BaseModel):
    email: EmailStr
    password: str

class WaresUpload(BaseModel):
    csv: str

# Security
api_key_cookie = APIKeyCookie(name="AUTH_COOKIE")

# Create tables
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                merchant_id INTEGER,
                FOREIGN KEY (merchant_id) REFERENCES merchants (id)
            )
        ''')
    print("Database initialized.")

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/merchants/register", status_code=201)
async def register_merchant(merchant: MerchantRegister):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
                         (merchant.email, merchant.name, merchant.password))
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already registered")
    return {"message": "Merchant registered successfully"}

@app.post("/merchants/login")
async def login_merchant(merchant: MerchantLogin, response: Response):
    with get_db_connection() as conn:
        merchant_data = conn.execute('SELECT * FROM merchants WHERE email = ? AND password = ?',
                                      (merchant.email, merchant.password)).fetchone()
        if not merchant_data:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        response.set_cookie(key="AUTH_COOKIE", value=merchant.email)
        return {"message": "Login successful"}

@app.post("/merchants/upload-wares")
async def upload_wares(wares: WaresUpload, request: Request):
    if not request.cookies.get("AUTH_COOKIE"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        csv_data = csv.reader(wares.csv.splitlines())
        next(csv_data)  # Skip header
        with get_db_connection() as conn:
            for row in csv_data:
                if len(row) != 3:
                    raise HTTPException(status_code=400, detail="Invalid CSV format")
                name, description, price = row
                conn.execute('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)',
                             (name, description, float(price)))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    
    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_class=HTMLResponse)
async def get_wares(minPrice: Optional[float] = None, maxPrice: Optional[float] = None, request: Request):
    if not request.cookies.get("AUTH_COOKIE"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = "SELECT * FROM wares"
    params = []
    if minPrice is not None:
        query += " WHERE price >= ?"
        params.append(minPrice)
    if maxPrice is not None:
        query += " AND price <= ?" if minPrice is not None else " WHERE price <= ?"
        params.append(maxPrice)

    with get_db_connection() as conn:
        wares = conn.execute(query, params).fetchall()
    
    html_content = "<table><tr><th>Name</th><th>Description</th><th>Price</th></tr>"
    for ware in wares:
        html_content += f"<tr><td>{ware['name']}</td><td>{ware['description']}</td><td>{ware['price']}</td></tr>"
    html_content += "</table>"
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)