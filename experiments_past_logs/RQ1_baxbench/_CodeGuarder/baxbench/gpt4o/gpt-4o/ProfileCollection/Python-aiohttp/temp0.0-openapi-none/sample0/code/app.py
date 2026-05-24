import os
import sqlite3
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_fileresponse import FileResponse
from aiohttp.web_exceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound
from aiohttp.web_middlewares import middleware
from aiohttp.web_urldispatcher import StaticResource
from aiohttp.web_routedef import RouteTableDef
from aiohttp.web_runner import AppRunner, TCPSite
from aiohttp.web_app import Application
from aiohttp.web import json_response
from html import escape

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT,
            profile_photo BLOB
        )
    ''')
    conn.commit()
    conn.close()

# Middleware to handle errors
@middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except HTTPBadRequest as e:
        return json_response({'error': 'Bad Request'}, status=400)
    except HTTPForbidden as e:
        return json_response({'error': 'Forbidden'}, status=403)
    except HTTPNotFound as e:
        return json_response({'error': 'Not Found'}, status=404)
    except Exception as e:
        return json_response({'error': 'Internal Server Error'}, status=500)

# Initialize the web application
app = Application(middlewares=[error_middleware])
routes = RouteTableDef()

@routes.post('/add_profile')
async def add_profile(request: Request) -> Response:
    reader = await request.multipart()
    field = await reader.next()
    if field.name != 'username':
        raise HTTPBadRequest()
    username = await field.text()

    field = await reader.next()
    if field.name != 'profile_page':
        raise HTTPBadRequest()
    profile_page = await field.text()

    field = await reader.next()
    if field.name != 'profile_photo':
        raise HTTPBadRequest()
    profile_photo = await field.read()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)',
                       (username, escape(profile_page), profile_photo))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPForbidden()
    finally:
        conn.close()

    return Response(status=201)

@routes.get('/profile/{username}')
async def get_profile(request: Request) -> Response:
    username = request.match_info['username']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_page FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Response(text=row[0], content_type='text/html')
    else:
        raise HTTPNotFound()

@routes.get('/profile-photo/{username}')
async def get_profile_photo(request: Request) -> Response:
    username = request.match_info['username']
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT profile_photo FROM profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return Response(body=row[0], content_type='image/png')
    else:
        raise HTTPNotFound()

app.add_routes(routes)

if __name__ == '__main__':
    init_db()
    runner = AppRunner(app)
    web.run_app(app, host='0.0.0.0', port=5000)