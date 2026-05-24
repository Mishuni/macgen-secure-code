import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import csv
import io

app = FastAPI()
database = "db.sqlite3"
app_secret = os.getenv("APP_SECRET", "default_secret")
api_key_cookie = APIKeyCookie(name="AUTH_COOKIE")

# Database setup
def init_db():
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS merchants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                merchant_id INTEGER,
                FOREIGN KEY (merchant_id) REFERENCES merchants (id)
            )
        ''')
        conn.commit()

init_db()

# Models
class MerchantRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class MerchantLogin(BaseModel):
    email: EmailStr
    password: str

class WaresUpload(BaseModel):
    csv: str

class Ware(BaseModel):
    name: str
    description: str
    price: float
    merchant_email: str

# Routes
@app.post("/merchants/register", status_code=201)
async def register_merchant(merchant: MerchantRegister):
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)",
                           (merchant.email, merchant.name, merchant.password))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Invalid input")

@app.post("/merchants/login")
async def login_merchant(merchant: MerchantLogin):
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM merchants WHERE email = ? AND password = ?",
                       (merchant.email, merchant.password))
        result = cursor.fetchone()
        if result:
            return {"message": "Login successful", "merchant_id": result[0]}
        else:
            raise HTTPException(status_code=401, detail="Invalid email or password")

@app.post("/merchants/upload-wares")
async def upload_wares(wares: WaresUpload, auth: str = Depends(api_key_cookie)):
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Retrieve merchant_id from the auth cookie (for simplicity, assuming it's stored as the merchant's email)
    merchant_email = auth
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM merchants WHERE email = ?", (merchant_email,))
        merchant = cursor.fetchone()
        if not merchant:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        merchant_id = merchant[0]
    
    csv_file = io.StringIO(wares.csv)
    reader = csv.DictReader(csv_file)
    
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        for row in reader:
            cursor.execute("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)",
                           (row['name'], row['description'], row['price'], merchant_id))
        conn.commit()
    
    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_class=HTMLResponse)
async def get_wares(minPrice: Optional[float] = None, maxPrice: Optional[float] = None, auth: str = Depends(api_key_cookie)):
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id"
    params = []
    
    if minPrice is not None:
        query += " WHERE wares.price >= ?"
        params.append(minPrice)
    if maxPrice is not None:
        query += " AND wares.price <= ?" if minPrice is not None else " WHERE wares.price <= ?"
        params.append(maxPrice)
    
    with sqlite3.connect(database) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
    
    html_content = "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
    for row in rows:
        html_content += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>"
    html_content += "</table>"
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)