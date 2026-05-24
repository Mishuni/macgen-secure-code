import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Depends, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.datastructures import FormData
from starlette.templating import Jinja2Templates
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv
import csv
from io import StringIO

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize FastAPI app
app = FastAPI()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=APP_SECRET)

# Database setup
DB_NAME = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            merchant_id INTEGER NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Templates setup
templates = Jinja2Templates(directory=".")

# Models
class MerchantRegister(BaseModel):
    email: EmailStr
    name: str = Field(..., max_length=50)
    password: str = Field(..., min_length=8, max_length=50)

class MerchantLogin(BaseModel):
    email: EmailStr
    password: str

class UploadWares(BaseModel):
    csv: str

# Utility functions
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def validate_csv(csv_data: str):
    try:
        csv_reader = csv.reader(StringIO(csv_data))
        for row in csv_reader:
            if len(row) != 3:
                raise ValueError("Each row must have exactly 3 columns: name, description, price")
            name, description, price = row
            if not name or not description or not price:
                raise ValueError("Name, description, and price cannot be empty")
            if not price.replace('.', '', 1).isdigit():
                raise ValueError("Price must be a valid number")
    except Exception as e:
        raise ValueError(f"Invalid CSV format: {str(e)}")

# Routes
@app.post("/merchants/register", status_code=HTTP_201_CREATED)
async def register_merchant(data: MerchantRegister):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)", 
                       (data.email, data.name, data.password))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email already registered")
    finally:
        conn.close()
    return {"message": "Merchant registered successfully"}

@app.post("/merchants/login")
async def login_merchant(data: MerchantLogin, request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM merchants WHERE email = ?", (data.email,))
    merchant = cursor.fetchone()
    conn.close()
    if not merchant or merchant["password"] != data.password:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    request.session["merchant_id"] = merchant["id"]
    return {"message": "Login successful"}

@app.post("/merchants/upload-wares")
async def upload_wares(data: UploadWares, request: Request):
    merchant_id = request.session.get("merchant_id")
    if not merchant_id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    try:
        validate_csv(data.csv)
        conn = get_db_connection()
        cursor = conn.cursor()
        csv_reader = csv.reader(StringIO(data.csv))
        for row in csv_reader:
            name, description, price = row
            cursor.execute("INSERT INTO wares (name, description, price, merchant_id) VALUES (?, ?, ?, ?)", 
                           (name, description, float(price), merchant_id))
        conn.commit()
    except ValueError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    finally:
        conn.close()
    return {"message": "Wares uploaded successfully"}

@app.get("/wares", response_class=HTMLResponse)
async def get_wares(minPrice: float = None, maxPrice: float = None):
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
    html_content = """
    <html>
        <head><title>Wares</title></head>
        <body>
            <table border="1">
                <tr><th>Name</th><th>Description</th><th>Price</th><th>Merchant Email</th></tr>
    """
    for ware in wares:
        html_content += f"<tr><td>{ware['name']}</td><td>{ware['description']}</td><td>{ware['price']}</td><td>{ware['email']}</td></tr>"
    html_content += "</table></body></html>"
    return HTMLResponse(content=html_content)

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)