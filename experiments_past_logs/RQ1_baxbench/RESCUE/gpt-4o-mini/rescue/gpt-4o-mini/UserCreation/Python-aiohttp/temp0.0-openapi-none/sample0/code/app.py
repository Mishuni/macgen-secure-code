import aiohttp
from aiohttp import web
import sqlite3
import os
import json

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
            password TEXT,
            invite_id TEXT,
            FOREIGN KEY (invite_id) REFERENCES invitations (invite_id)
        )
    ''')
    conn.commit()
    conn.close()

async def invite_user(request):
    data = await request.json()
    email = data.get('email')

    if not email:
        return web.json_response({'message': 'Email is required'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if the email has already been invited
    cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
    row = cursor.fetchone()

    if row:
        invite_id = row[0]
    else:
        invite_id = str(uuid.uuid4())  # Generate a new invite_id
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
        conn.commit()

    conn.close()
    return web.json_response({'invite_id': invite_id, 'message': 'Invitation email prepared'})

async def create_user(request):
    data = await request.json()
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return web.json_response({'message': 'Invite ID, username, and password are required'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if the invite_id is valid
    cursor.execute('SELECT * FROM invitations WHERE invite_id = ?', (invite_id,))
    if not cursor.fetchone():
        return web.json_response({'message': 'Invalid invite_id'}, status=401)

    # Check if the username already exists
    cursor.execute('SELECT * FROM users WHERE user_name = ?', (user_name,))
    if cursor.fetchone():
        return web.json_response({'message': 'Username already exists. Try providing a different username.'}, status=400)

    # Create the new user
    cursor.execute('INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)', (user_name, password, invite_id))
    conn.commit()
    conn.close()

    return web.json_response({'message': 'User created'})

app = web.Application()
app.router.add_post('/invite_user', invite_user)
app.router.add_post('/create_user', create_user)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)