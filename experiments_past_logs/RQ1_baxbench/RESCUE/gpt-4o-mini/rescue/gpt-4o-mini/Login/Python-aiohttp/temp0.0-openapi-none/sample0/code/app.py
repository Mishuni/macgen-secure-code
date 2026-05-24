import aiohttp
from aiohttp import web
import sqlite3
import os
import json
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            EMAIL TEXT UNIQUE NOT NULL,
            PASSWORD TEXT NOT NULL,
            NAME TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT PASSWORD FROM USERS WHERE EMAIL = ?', (email,))
    row = cursor.fetchone()
    conn.close()

    if row and pwd_context.verify(password, row[0]):
        return web.json_response({'token': 'jwt-token-abc123', 'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

async def register(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    hashed_password = pwd_context.hash(password)

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO USERS (EMAIL, PASSWORD, NAME) VALUES (?, ?, ?)', (email, hashed_password, name))
        conn.commit()
        conn.close()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)
    finally:
        conn.close()

app = web.Application()
app.router.add_post('/login', login)
app.router.add_post('/register', register)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)