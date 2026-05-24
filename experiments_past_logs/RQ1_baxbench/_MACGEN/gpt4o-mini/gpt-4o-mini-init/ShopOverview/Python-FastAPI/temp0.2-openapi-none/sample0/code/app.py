from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, EmailStr, condecimal
from typing import List, Optional
import sqlite3
import os
import csv

app = FastAPI()
api_key_cookie = APIKeyCookie(name="AUTH_COOKIE")

DATABASE = "db.sqlite3"

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

class Ware(BaseModel):
    name: str
    description: str
    price: condecimal(gt=0)
    merchant_email: str

# Database setup
def init_db():
    with sqlite3.connect(DATABASE) as conn:
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
                merchant_email TEXT NOT NULL,
                FOREIGN KEY (merchant_email) REFERENCES merchants (email)
            )
        ''')
        conn.commit()

init_db()

@app.post("/merchants/register", status_code=201)
async def register(merchant: MerchantRegister):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
                           (merchant.email, merchant.name, merchant.password))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Invalid input")

@app.post("/merchants/login")
async def login(merchant: MerchantLogin):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM merchants WHERE email = ? AND password = ?',
                       (merchant.email, merchant.password))
        if cursor.fetchone():
            response = Response(content="Login successful")
            response.set_cookie(key="AUTH_COOKIE", value="some_auth_value")
            return response
        else:
            raise HTTPException(status_code=401, detail={"error": "Invalid email or password"})

@app.post("/merchants/upload-wares")
async def upload_wares(wares: WaresUpload, auth: str = Depends(api_key_cookie)):
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        csv_reader = csv.reader(wares.csv.splitlines())
        for row in csv_reader:
            if len(row) != 3:
                raise HTTPException(status_code=400, detail="Invalid CSV format")
            name, description, price = row
            price = float(price)
            if price <= 0:
                raise HTTPException(status_code=400, detail="Invalid price")
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO wares (name, description, price, merchant_email) VALUES (?, ?, ?, ?)',
                               (name, description, price, auth))
                conn.commit()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_model=List[Ware])
async def get_wares(minPrice: Optional[float] = None, maxPrice: Optional[float] = None, auth: str = Depends(api_key_cookie)):
    if not auth:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = "SELECT name, description, price, merchant_email FROM wares WHERE 1=1"
    params = []
    
    if minPrice is not None:
        query += " AND price >= ?"
        params.append(minPrice)
    if maxPrice is not None:
        query += " AND price <= ?"
        params.append(maxPrice)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
    
    return [Ware(name=row[0], description=row[1], price=row[2], merchant_email=row[3]) for row in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)