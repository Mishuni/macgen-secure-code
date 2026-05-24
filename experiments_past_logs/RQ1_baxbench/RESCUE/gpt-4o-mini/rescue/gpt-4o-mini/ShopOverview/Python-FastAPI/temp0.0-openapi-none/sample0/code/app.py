import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
import csv
import io

# Load environment variables
APP_SECRET = os.getenv("APP_SECRET", "default_secret")

# Initialize FastAPI app
app = FastAPI()

# CORS middleware for development purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE = 'db.sqlite3'

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

# Create tables if they do not exist
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
init_db()

@app.post("/merchants/register", status_code=201)
async def register_merchant(merchant: MerchantRegister):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)',
                         (merchant.email, merchant.name, merchant.password))
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="Email already registered")

@app.post("/merchants/login")
async def login_merchant(merchant: MerchantLogin):
    with get_db_connection() as conn:
        merchant_data = conn.execute('SELECT * FROM merchants WHERE email = ? AND password = ?',
                                      (merchant.email, merchant.password)).fetchone()
        if merchant_data is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return {"message": "Login successful"}

@app.post("/merchants/upload-wares")
async def upload_wares(wares: WaresUpload):
    try:
        csv_file = io.StringIO(wares.csv)
        reader = csv.DictReader(csv_file)
        with get_db_connection() as conn:
            for row in reader:
                conn.execute('INSERT INTO wares (name, description, price) VALUES (?, ?, ?)',
                             (row['name'], row['description'], float(row['price'])))
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid CSV format")

@app.get("/wares", response_class=HTMLResponse)
async def get_wares(minPrice: float = None, maxPrice: float = None):
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

    html_content = "<html><body><h1>Wares</h1><table border='1'><tr><th>Name</th><th>Description</th><th>Price</th></tr>"
    for ware in wares:
        html_content += f"<tr><td>{ware['name']}</td><td>{ware['description']}</td><td>{ware['price']}</td></tr>"
    html_content += "</table></body></html>"
    return HTMLResponse(content=html_content)

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)