import os
import sqlite3
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
import csv
import io
import bcrypt

app = FastAPI()
db_path = "db.sqlite3"

# Initialize database
def init_db():
    with sqlite3.connect(db_path) as conn:
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
                merchant_id INTEGER,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (merchant_id) REFERENCES merchants (id)
            )
        ''')
        conn.commit()

init_db()

# Security
api_key_cookie = APIKeyCookie(name="AUTH_COOKIE")

# Models
class MerchantRegister(BaseModel):
    email: EmailStr
    name: str
    password: constr(min_length=8, regex="(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])")  # Strong password policy

class MerchantLogin(BaseModel):
    email: EmailStr
    password: str

class WaresUpload(BaseModel):
    csv: str

# Routes
@app.post("/merchants/register", status_code=201)
async def register_merchant(merchant: MerchantRegister):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            hashed_password = bcrypt.hashpw(merchant.password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)",
                           (merchant.email, merchant.name, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already registered")

@app.post("/merchants/login")
async def login_merchant(merchant: MerchantLogin):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM merchants WHERE email = ?", (merchant.email,))
        result = cursor.fetchone()
        if result is None or not bcrypt.checkpw(merchant.password.encode('utf-8'), result[1].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {"message": "Login successful", "merchant_id": result[0]}  # Return merchant ID for further use

@app.post("/merchants/upload-wares")
async def upload_wares(wares: WaresUpload, auth: str = Depends(api_key_cookie)):
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        csv_file = io.StringIO(wares.csv)
        reader = csv.DictReader(csv_file)
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            for row in reader:
                # Validate CSV data
                if 'name' not in row or 'description' not in row or 'price' not in row:
                    raise HTTPException(status_code=400, detail="Invalid CSV format")
                try:
                    price = float(row['price'])
                except ValueError:
                    raise HTTPException(status_code=400, detail="Price must be a valid number")
                
                # Retrieve merchant_id from auth (this is a placeholder, implement actual retrieval)
                merchant_id = 1  # Replace with actual merchant ID retrieval logic
                cursor.execute("INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)",
                               (merchant_id, row['name'], row['description'], price))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    
    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_class=HTMLResponse)
async def get_wares(minPrice: Optional[float] = None, maxPrice: Optional[float] = None, auth: str = Depends(api_key_cookie)):
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = "SELECT w.name, w.description, w.price, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id"
    filters = []
    params = []
    
    if minPrice is not None:
        filters.append("w.price >= ?")
        params.append(minPrice)
    if maxPrice is not None:
        filters.append("w.price <= ?")
        params.append(maxPrice)
    
    if filters:
        query += " WHERE " + " AND ".join(filters)
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        wares = cursor.fetchall()
    
    html_content = "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
    for ware in wares:
        html_content += f"<tr><td>{ware[0]}</td><td>{ware[1]}</td><td>{ware[2]}</td><td>{ware[3]}</td></tr>"
    html_content += "</table>"
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)