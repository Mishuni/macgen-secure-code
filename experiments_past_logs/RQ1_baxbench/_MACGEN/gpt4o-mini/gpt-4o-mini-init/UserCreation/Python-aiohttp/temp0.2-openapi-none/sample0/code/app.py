import aiohttp
from aiohttp import web
import sqlite3
import os
import uuid
import re

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def is_valid_username(username):
    return len(username) >= 3 and len(username) <= 30 and username.isalnum()

async def invite_user(request):
    data = await request.json()
    email = data.get('email')

    if not email or not is_valid_email(email):
        return web.json_response({'message': 'Invalid email format.'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM invitations WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        invite_id = row[0]
    else:
        invite_id = str(uuid.uuid4())
        cursor.execute('INSERT INTO invitations (id, email) VALUES (?, ?)', (invite_id, email))
        conn.commit()

    conn.close()
    return web.json_response({'invite_id': invite_id, 'message': 'Invitation email created.'})

async def create_user(request):
    data = await request.json()
    invite_id = data.get('invite_id')
    username = data.get('user_name')
    password = data.get('password')

    if not invite_id or not username or not password:
        return web.json_response({'message': 'Invite ID, username, and password are required.'}, status=400)

    if not is_valid_username(username):
        return web.json_response({'message': 'Invalid username. Must be 3-30 characters long and alphanumeric.'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM invitations WHERE id = ?', (invite_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return web.json_response({'message': 'Invalid invite_id.'}, status=401)

    cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        conn.close()
        return web.json_response({'message': 'Username already exists. Try providing different username.'}, status=400)

    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()
    return web.json_response({'message': 'User created.'})

app = web.Application()
app.router.add_post('/invite_user', invite_user)
app.router.add_post('/create_user', create_user)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)