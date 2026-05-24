import os
import sqlite3
from aiohttp import web
import json
import re

DATABASE = 'db.sqlite3'
APP_SECRET = os.getenv('APP_SECRET', 'default_secret')

# Initialize the database
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

# Utility function to validate email
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Endpoint to create an invitation
async def invite_user(request):
    try:
        data = await request.json()
        email = data.get('email')

        if not email or not is_valid_email(email):
            return web.json_response({'message': 'Invalid email format'}, status=400)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('SELECT invite_id FROM invitations WHERE email = ?', (email,))
        row = cursor.fetchone()

        if row:
            invite_id = row[0]
        else:
            invite_id = os.urandom(16).hex()
            cursor.execute('INSERT INTO invitations (email, invite_id) VALUES (?, ?)', (email, invite_id))
            conn.commit()

        conn.close()
        return web.json_response({'invite_id': invite_id, 'message': 'Invitation created successfully'}, status=200)

    except Exception as e:
        return web.json_response({'message': str(e)}, status=500)

# Endpoint to create a user
async def create_user(request):
    try:
        data = await request.json()
        invite_id = data.get('invite_id')
        user_name = data.get('user_name')
        password = data.get('password')

        if not invite_id or not user_name or not password:
            return web.json_response({'message': 'Missing required fields'}, status=400)

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute('SELECT email FROM invitations WHERE invite_id = ?', (invite_id,))
        row = cursor.fetchone()

        if not row:
            return web.json_response({'message': 'Invalid invite_id'}, status=401)

        cursor.execute('SELECT user_name FROM users WHERE user_name = ?', (user_name,))
        if cursor.fetchone():
            return web.json_response({'message': 'Username already exists. Try providing different username.'}, status=400)

        cursor.execute('INSERT INTO users (user_name, password) VALUES (?, ?)', (user_name, password))
        conn.commit()
        conn.close()

        return web.json_response({'message': 'User created successfully'}, status=200)

    except Exception as e:
        return web.json_response({'message': str(e)}, status=500)

# Set up the web application
app = web.Application()
app.router.add_post('/invite_user', invite_user)
app.router.add_post('/create_user', create_user)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)