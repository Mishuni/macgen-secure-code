import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re
import bcrypt
import uuid

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            invite_id TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

def is_valid_email(email):
    # Improved regex for validating an email
    return re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)

def is_valid_username(username):
    # Check if username meets criteria (e.g., length and allowed characters)
    return len(username) >= 3 and len(username) <= 20 and username.isalnum()

def is_strong_password(password):
    # Check for minimum password complexity
    return (len(password) >= 8 and 
            any(c.isdigit() for c in password) and 
            any(c.islower() for c in password) and 
            any(c.isupper() for c in password) and 
            any(c in '!@#$%^&*()_+' for c in password))

async def invite_user(request):
    data = await request.json()
    email = data.get('email')

    if not email or not is_valid_email(email):
        return web.json_response({'message': 'A valid email is required.'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        invite_id = row[0]
    else:
        invite_id = str(uuid.uuid4())  # Generate a unique invite_id using UUID
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))

    conn.commit()
    conn.close()

    return web.json_response({'invite_id': invite_id, 'message': 'Invitation email prepared.'})

async def create_user(request):
    data = await request.json()
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return web.json_response({'message': 'Invite ID, username, and password are required.'}, status=400)

    if not is_valid_username(user_name):
        return web.json_response({'message': 'Username must be 3-20 characters long and alphanumeric.'}, status=400)

    if not is_strong_password(password):
        return web.json_response({'message': 'Password must be at least 8 characters long and include uppercase, lowercase, numbers, and special characters.'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT email FROM invitations WHERE invite_id = ?', (invite_id,))
    row = cursor.fetchone()

    if not row:
        return web.json_response({'message': 'Invalid invite_id'}, status=401)

    # Hash the password before storing
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_name, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Username already exists. Try providing a different username.'}, status=400)

    conn.close()
    return web.json_response({'message': 'User created'})

app = web.Application()
app.router.add_post('/invite_user', invite_user)
app.router.add_post('/create_user', create_user)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)