import os
import sqlite3
from aiohttp import web
import json
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS USERS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SECRETS (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                secret TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES USERS (username)
            )
        ''')
        conn.commit()

# Initialize the database
init_db()

async def register(request):
    data = await request.json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')

    if not email or not username or not password:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)

    hashed_password = pwd_context.hash(password)

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO USERS (email, username, password) VALUES (?, ?, ?)', 
                           (email, username, hashed_password))
            conn.commit()
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)

    return web.json_response({'message': 'Registration successful'}, status=201)

async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM USERS WHERE email = ?', (email,))
        row = cursor.fetchone()

    if row and pwd_context.verify(password, row[0]):
        return web.json_response({'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

async def set_secret(request):
    data = await request.json()
    username = data.get('username')
    secret = data.get('secret')

    if not username or not secret:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO SECRETS (username, secret) VALUES (?, ?)', 
                       (username, secret))
        conn.commit()

    return web.json_response({'message': 'Secret has been set successfully'}, status=200)

async def get_secret(request):
    username = request.query.get('username')

    if not username:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT secret FROM SECRETS WHERE username = ?', (username,))
        row = cursor.fetchone()

    if row:
        return web.json_response({'secret': row[0]}, status=200)
    else:
        return web.json_response({'message': 'Invalid authentication token'}, status=401)

app = web.Application()
app.router.add_post('/register', register)
app.router.add_post('/login', login)
app.router.add_post('/set_secret', set_secret)
app.router.add_get('/get_secret', get_secret)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)