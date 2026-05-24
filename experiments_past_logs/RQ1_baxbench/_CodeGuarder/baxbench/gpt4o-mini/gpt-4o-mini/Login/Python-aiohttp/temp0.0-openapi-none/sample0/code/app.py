import os
import json
import sqlite3
from aiohttp import web
from passlib.context import CryptContext
import jwt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
APP_SECRET = os.getenv('APP_SECRET', 'default_secret')

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# User registration
async def register(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not email or not password or not name:
        return web.json_response({'message': 'Email, password, and name are required.'}, status=400)

    hashed_password = pwd_context.hash(password)

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, hashed_password, name))
        conn.commit()
        conn.close()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)

# User login
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return web.json_response({'message': 'Email and password are required.'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and pwd_context.verify(password, user[0]):
        token = jwt.encode({'email': email}, APP_SECRET, algorithm='HS256')
        return web.json_response({'token': token, 'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

# Initialize web application
app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)