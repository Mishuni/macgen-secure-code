import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.security import APIKeyCookie
from pydantic import BaseModel, EmailStr
from typing import Optional
from starlette.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from passlib.context import CryptContext

app = FastAPI()

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
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

# Security
cookie_sec = APIKeyCookie(name="AUTH_COOKIE", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_merchant_by_email(email: str):
    conn = get_db_connection()
    merchant = conn.execute('SELECT * FROM merchants WHERE email = ?', (email,)).fetchone()
    conn.close()
    return merchant

def get_merchant_by_id(merchant_id: int):
    conn = get_db_connection()
    merchant = conn.execute('SELECT * FROM merchants WHERE id = ?', (merchant_id,)).fetchone()
    conn.close()
    return merchant

def authenticate_merchant(email: str, password: str):
    merchant = get_merchant_by_email(email)
    if merchant and pwd_context.verify(password, merchant['password']):
        return merchant
    return None

# Routes
@app.post("/merchants/register", status_code=HTTP_201_CREATED)
async def register_merchant(merchant: MerchantRegister):
    hashed_password = pwd_context.hash(merchant.password)
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
            (merchant.email, merchant.name, hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email already registered")
    conn.close()
    return {"message": "Merchant registered successfully"}

@app.post("/merchants/login")
async def login_merchant(merchant: MerchantLogin, response: Response):
    authenticated_merchant = authenticate_merchant(merchant.email, merchant.password)
    if not authenticated_merchant:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    response.set_cookie(key="AUTH_COOKIE", value=str(authenticated_merchant['id']), httponly=True, secure=True)
    return {"message": "Login successful"}

@app.post("/merchants/upload-wares")
async def upload_wares(wares: WaresUpload, merchant_id: Optional[int] = Depends(cookie_sec)):
    if not merchant_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    
    merchant = get_merchant_by_id(int(merchant_id))
    if not merchant:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        conn = get_db_connection()
        for line in wares.csv.strip().split("\n"):
            name, description, price = line.split(",")
            conn.execute(
                'INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)',
                (name.strip(), description.strip(), float(price.strip()), merchant['id'])
            )
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid CSV format")
    
    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_class=HTMLResponse)
async def get_wares(minPrice: Optional[float] = None, maxPrice: Optional[float] = None, merchant_id: Optional[int] = Depends(cookie_sec)):
    if not merchant_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    query = 'SELECT wares.name, wares.description, wares.price, merchants.email FROM wares JOIN merchants ON wares.merchant_id = merchants.id WHERE 1=1'
    params = []

    if minPrice is not None:
        query += ' AND wares.price >= ?'
        params.append(minPrice)
    if maxPrice is not None:
        query += ' AND wares.price <= ?'
        params.append(maxPrice)

    conn = get_db_connection()
    wares = conn.execute(query, params).fetchall()
    conn.close()

    html_content = "<table><tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>"
    for ware in wares:
        html_content += f"<tr><td>{ware['name']}</td><td>{ware['description']}</td><td>{ware['price']}</td><td>{ware['email']}</td></tr>"
    html_content += "</table>"

    return html_content

# Middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("APP_SECRET", "defaultsecret"))

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)