import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Aiohttp application
app = web.Application()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

async def login(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not is_valid_email(email) or not password:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        return web.json_response({'token': 'jwt-token-abc123', 'message': 'Login successful'}, status=200)
    else:
        return web.json_response({'message': 'Invalid email or password'}, status=401)

async def register(request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')

    if not is_valid_email(email) or not password or not name:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, password, name))
        conn.commit()
        return web.json_response({'message': 'Registration successful'}, status=201)
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Email already in use or invalid data'}, status=400)
    finally:
        conn.close()

app.router.add_post('/login', login)
app.router.add_post('/register', register)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)