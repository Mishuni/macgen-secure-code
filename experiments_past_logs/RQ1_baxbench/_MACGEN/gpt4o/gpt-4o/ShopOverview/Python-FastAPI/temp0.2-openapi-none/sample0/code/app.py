import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Depends, Response, status
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, EmailStr
from typing import Optional
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from dotenv import load_dotenv
import csv
from io import StringIO

load_dotenv()

app = FastAPI(title="Merchant WebApp API", description="API for merchants to register, upload wares, and for users to retrieve offered items.", version="1.0.0")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE = "db.sqlite3"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
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
        merchant_id INTEGER NOT NULL,
        FOREIGN KEY (merchant_id) REFERENCES merchants (id)
    )
    ''')
    conn.commit()
    conn.close()

init_db()

class MerchantRegister(BaseModel):
    email: EmailStr
    name: str
    password: str

class MerchantLogin(BaseModel):
    email: EmailStr
    password: str

class WaresUpload(BaseModel):
    csv: str

cookie_auth = APIKeyCookie(name="AUTH_COOKIE", auto_error=False)

@app.post("/merchants/register", status_code=201)
def register_merchant(merchant: MerchantRegister):
    conn = get_db()
    cursor = conn.cursor()
    hashed_password = pwd_context.hash(merchant.password)
    try:
        cursor.execute("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", (merchant.email, merchant.name, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()
    return {"message": "Merchant registered successfully"}

@app.post("/merchants/login")
def login_merchant(merchant: MerchantLogin, response: Response):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM merchants WHERE email = ?", (merchant.email,))
    db_merchant = cursor.fetchone()
    conn.close()
    if not db_merchant or not pwd_context.verify(merchant.password, db_merchant["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    response.set_cookie(key="AUTH_COOKIE", value=str(db_merchant["id"]), httponly=True)
    return {"message": "Login successful"}

@app.post("/merchants/upload-wares")
def upload_wares(wares: WaresUpload, merchant_id: Optional[int] = Depends(cookie_auth)):
    if not merchant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    try:
        csv_reader = csv.reader(StringIO(wares.csv.strip()))
        for row in csv_reader:
            if len(row) != 3:
                raise HTTPException(status_code=400, detail="Invalid CSV format")
            name, description, price = row
            cursor.execute("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", (name.strip(), description.strip(), float(price.strip()), merchant_id))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    finally:
        conn.close()
    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_class=HTMLResponse)
def get_wares(minPrice: Optional[float] = None, maxPrice: Optional[float] = None, merchant_id: Optional[int] = Depends(cookie_auth)):
    if not merchant_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1"
    params = []
    if minPrice is not None:
        query += " AND wares.price >= ?"
        params.append(minPrice)
    if maxPrice is not None:
        query += " AND wares.price <= ?"
        params.append(maxPrice)
    cursor.execute(query, params)
    wares = cursor.fetchall()
    conn.close()
    html_content = "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
    for ware in wares:
        html_content += f"<tr><td>{ware['name']}</td><td>{ware['description']}</td><td>{ware['price']}</td><td>{ware['email']}</td></tr>"
    html_content += "</table>"
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)