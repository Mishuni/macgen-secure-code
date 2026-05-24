import os
import sqlite3
import aiohttp
from aiohttp import web
from passlib.hash import bcrypt
import re
import logging
import ssl

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            email TEXT PRIMARY KEY,
            invite_id TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_name TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Helper functions
def generate_invite_id(email):
    secret = os.getenv('APP_SECRET')
    if not secret:
        raise RuntimeError("APP_SECRET environment variable is not set")
    return bcrypt.hash(email + secret)

def create_invitation(email):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
    row = cursor.fetchone()
    if row:
        invite_id = row[0]
    else:
        invite_id = generate_invite_id(email)
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
        conn.commit()
    conn.close()
    return invite_id

def create_user(invite_id, user_name, password):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM invitations WHERE invite_id = ?', (invite_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False, 'Invalid invite_id'
    
    cursor.execute('SELECT user_name FROM users WHERE user_name = ?', (user_name,))
    if cursor.fetchone():
        conn.close()
        return False, 'User already exists'
    
    hashed_password = bcrypt.hash(password)
    cursor.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_name, hashed_password))
    conn.commit()
    conn.close()
    return True, 'User created successfully'

def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_password(password):
    # Stronger password policy
    return (len(password) >= 8 and
            re.search(r"[A-Z]", password) and
            re.search(r"[a-z]", password) and
            re.search(r"[0-9]", password) and
            re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

# API Handlers
async def invite_user(request):
    data = await request.json()
    email = data.get('email')
    if not email or not validate_email(email):
        return web.json_response({'message': 'Invalid email format'}, status=400)
    
    invite_id = create_invitation(email)
    return web.json_response({'invite_id': invite_id, 'message': 'Invitation created'})

async def create_user_handler(request):
    data = await request.json()
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')
    
    if not invite_id or not user_name or not password:
        return web.json_response({'message': 'All fields are required'}, status=400)
    
    if not validate_password(password):
        return web.json_response({'message': 'Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters'}, status=400)
    
    success, message = create_user(invite_id, user_name, password)
    if success:
        return web.json_response({'message': message})
    else:
        return web.json_response({'message': 'Invalid invite_id or user already exists'}, status=400)

# App setup
app = web.Application()
app.router.add_post('/invite_user', invite_user)
app.router.add_post('/create_user', create_user_handler)

if __name__ == '__main__':
    init_db()
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='path/to/certfile', keyfile='path/to/keyfile')
    web.run_app(app, host='0.0.0.0', port=5000, ssl_context=ssl_context)