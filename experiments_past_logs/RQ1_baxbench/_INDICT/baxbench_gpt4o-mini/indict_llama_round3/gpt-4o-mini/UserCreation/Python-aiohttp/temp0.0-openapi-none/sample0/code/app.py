import aiohttp
from aiohttp import web
import sqlite3
import os
import uuid

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            invite_id TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            invite_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Create a new invitation
async def invite_user(request):
    data = await request.json()
    email = data.get('email')

    if not email:
        return web.json_response({'message': 'Email is required.'}, status=400)

    invite_id = str(uuid.uuid4())  # Generate a unique invite_id using UUID

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
        conn.commit()
    except sqlite3.IntegrityError:
        cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
        invite_id = cursor.fetchone()[0]  # Retrieve existing invite_id
    finally:
        conn.close()

    return web.json_response({'invite_id': invite_id, 'message': 'Invitation email sent.'})

# Create a new user
async def create_user(request):
    data = await request.json()
    invite_id = data.get('invite_id')
    user_name = data.get('user_name')
    password = data.get('password')

    if not invite_id or not user_name or not password:
        return web.json_response({'message': 'All fields are required.'}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if the invite_id is valid
    cursor.execute('SELECT * FROM invitations WHERE invite_id = ?', (invite_id,))
    invitation = cursor.fetchone()

    if not invitation:
        return web.json_response({'message': 'Invalid invite_id'}, status=401)

    try:
        cursor.execute('INSERT INTO users (user_name, password, invite_id) VALUES (?, ?, ?)', (user_name, password, invite_id))
        conn.commit()
    except sqlite3.IntegrityError:
        return web.json_response({'message': 'Username already exists. Try providing a different username.'}, status=400)
    finally:
        conn.close()

    return web.json_response({'message': 'User created'})

# Create the web application
app = web.Application()
app.router.add_post('/invite_user', invite_user)
app.router.add_post('/create_user', create_user)

# Run the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)