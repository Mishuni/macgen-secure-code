import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Response, Depends, Cookie, Form
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, EmailStr, constr, condecimal
from starlette.responses import HTMLResponse
from passlib.context import CryptContext
from dotenv import load_dotenv
from typing import Optional
import html

load_dotenv()

app = FastAPI()

# Database setup
DATABASE = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
cookie_auth = APIKeyCookie(name="AUTH_COOKIE", auto_error=False)

# Models
class MerchantRegister(BaseModel):
    email: EmailStr
    name: constr(min_length=1, max_length=100)
    password: constr(min_length=8)

class MerchantLogin(BaseModel):
    email: EmailStr
    password: str

class UploadWares(BaseModel):
    csv: str

# Helper functions
def create_tables():
    conn = get_db_connection()
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

def get_merchant_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM merchants WHERE email = ?", (email,))
    merchant = cursor.fetchone()
    conn.close()
    return merchant

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def validate_csv_line(line: str):
    # Basic CSV line validation
    parts = line.split(',')
    if len(parts) != 3:
        raise ValueError("CSV line must have exactly three parts")
    name, description, price = parts
    if not name.strip() or not description.strip():
        raise ValueError("Name and description cannot be empty")
    try:
        float(price.strip())
    except ValueError:
        raise ValueError("Price must be a valid number")

# Routes
@app.post("/merchants/register", status_code=201)
async def register_merchant(merchant: MerchantRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)",
            (merchant.email, merchant.name, hash_password(merchant.password))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    conn.close()
    return {"message": "Merchant registered successfully"}

@app.post("/merchants/login")
async def login_merchant(merchant: MerchantLogin, response: Response):
    db_merchant = get_merchant_by_email(merchant.email)
    if not db_merchant or not verify_password(merchant.password, db_merchant["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    response.set_cookie(key="AUTH_COOKIE", value=str(db_merchant["id"]), httponly=True, secure=True, samesite='Strict')
    return {"message": "Login successful"}

@app.post("/merchants/upload-wares")
async def upload_wares(wares: UploadWares, auth_cookie: Optional[str] = Depends(cookie_auth)):
    if not auth_cookie:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    merchant = get_merchant_by_email(auth_cookie)
    if not merchant:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        for line in wares.csv.splitlines():
            validate_csv_line(line)
            name, description, price = line.split(',')
            cursor.execute(
                "INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)",
                (name.strip(), description.strip(), float(price.strip()), merchant["id"])
            )
        conn.commit()
    except ValueError as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    except sqlite3.Error as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Database error")
    conn.close()
    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_class=HTMLResponse)
async def get_wares(minPrice: Optional[float] = None, maxPrice: Optional[float] = None, auth_cookie: Optional[str] = Depends(cookie_auth)):
    if not auth_cookie:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    conn = get_db_connection()
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
        html_content += f"<tr><td>{html.escape(ware['name'])}</td><td>{html.escape(ware['description'])}</td><td>{ware['price']}</td><td>{html.escape(ware['email'])}</td></tr>"
    html_content += "</table>"
    return html_content

# Initialize database
create_tables()

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)