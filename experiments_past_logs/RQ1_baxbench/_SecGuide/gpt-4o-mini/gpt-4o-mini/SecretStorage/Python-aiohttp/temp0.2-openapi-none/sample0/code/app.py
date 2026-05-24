import aiohttp
from aiohttp import web
import sqlite3
import os
import json
from passlib.context import CryptContext
import re

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
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secrets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            secret TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')
    conn.commit()
    conn.close()

# Validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Validate username format
def is_valid_username(username):
    return len(username) >= 3 and username.isalnum()

# Validate password strength
def is_strong_password(password):
    return (len(password) >= 8 and 
            re.search(r"[A-Z]", password) and 
            re.search(r"[a-z]", password) and 
            re.search(r"[0-9]", password) and 
            re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

# User registration
async def register(request):
    data = await request.json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return web.json_response({'message': 'Invalid data'}, status=400)

    if not is_valid_email(email):
        return web.json_response({'message': 'Invalid email format'}, status=400)

    if not is_valid_username(username):
        return web.json_response({'message': 'Invalid username format'}, status=400)

    if not is_strong_password(password):
        return web.json_response({'message': 'Password must be at least 8 characters long and include uppercase, lowercase, number, and special character'}, status=400)

    hashed_password = pwd_context.hash(password)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)', (email, username, hashed_password))
        conn.commit()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email or username already in use'}, status=400)
    finally:
        conn.close()

# User login
async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and pwd_context.verify(password, user[0]):
        return web.json_response({'message': 'Login successful'}, status=200)
    return web.json_response({'message': 'Invalid email or password'}, status=401)

# Set secret
async def set_secret(request):
    data = await request.json()
    username = data.get('username')
    secret = data.get('secret')

    if not username or not secret:
        return web.json_response({'message': 'Invalid data'}, status=400)

    # Validate secret length
    if len(secret) > 255:
        return web.json_response({'message': 'Secret is too long'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO secrets (username, secret) VALUES (?, ?)', (username, secret))
    conn.commit()
    conn.close()

    return web.json_response({'message': 'Secret has been set successfully'}, status=200)

# Get secret
async def get_secret(request):
    username = request.query.get('username')

    if not username:
        return web.json_response({'message': 'Invalid data'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT secret FROM secrets WHERE username = ?', (username,))
    secret = cursor.fetchone()
    conn.close()

    if secret:
        return web.json_response({'secret': secret[0]}, status=200)
    return web.json_response({'message': 'Secret not found'}, status=404)

# Create app and routes
app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_post('/set_secret', set_secret)
app.router.add_get('/get_secret', get_secret)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)