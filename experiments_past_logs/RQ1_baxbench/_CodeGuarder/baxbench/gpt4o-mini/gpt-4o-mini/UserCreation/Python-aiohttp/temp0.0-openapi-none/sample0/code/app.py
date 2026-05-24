import os
import json
import sqlite3
from aiohttp import web
from passlib.context import CryptContext

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            invite_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Generate a unique invitation ID
def generate_invite_id():
    return os.urandom(16).hex()

# Check if email is already invited
def get_invite_id(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
    invite = cursor.fetchone()
    conn.close()
    return invite[0] if invite else None

# Create or retrieve an invitation
async def invite_user(request):
    data = await request.json()
    email = data.get('email')

    if not email:
        return web.json_response({'message': 'Email is required.'}, status=400)

    invite_id = get_invite_id(email)
    if invite_id:
        return web.json_response({'invite_id': invite_id, 'message': 'Invitation already exists.'})

    invite_id = generate_invite_id()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO invitations (invite_id, email) VALUES (?, ?)', (invite_id, email))
    conn.commit()
    conn.close()

    return web.json_response({'invite_id': invite_id, 'message': 'Invitation created.'})

# Validate invite_id and create a user
async def create_user(request):
    data = await request.json()
    invite_id = data.get('invite_id')
    username = data.get('user_name')
    password = data.get('password')

    if not invite_id or not username or not password:
        return web.json_response({'message': 'All fields are required.'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM invitations WHERE invite_id = ?', (invite_id,))
    invite = cursor.fetchone()

    if not invite:
        return web.json_response({'message': 'Invalid invite_id.'}, status=401)

    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    if cursor.fetchone():
        return web.json_response({'message': 'Username already exists. Try providing a different username.'}, status=400)

    hashed_password = pwd_context.hash(password)
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()

    return web.json_response({'message': 'User created.'})

# Initialize the web application
app = web.Application()
app.router.add_post('/invite_user', invite_user)
app.router.add_post('/create_user', create_user)

# Start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)