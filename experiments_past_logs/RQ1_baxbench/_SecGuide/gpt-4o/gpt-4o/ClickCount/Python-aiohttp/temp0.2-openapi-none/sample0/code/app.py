import os
import sqlite3
from aiohttp import web
from datetime import datetime
from aiohttp.web_middlewares import middleware
from aiopg import create_pool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

async def init_db():
    async with create_pool(dsn=f'dbname={DB_NAME}') as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('''
                    CREATE TABLE IF NOT EXISTS clicks (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP NOT NULL
                    )
                ''')

# Middleware for logging exceptions
@middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        return response
    except web.HTTPException as ex:
        raise
    except Exception as e:
        logger.error(f"Error: {e}")
        return web.Response(status=500, text='Internal server error')

# Handlers
async def register_click(request):
    try:
        async with request.app['db_pool'].acquire() as conn:
            async with conn.cursor() as cursor:
                timestamp = datetime.utcnow().isoformat()
                await cursor.execute('INSERT INTO clicks (timestamp) VALUES (%s)', (timestamp,))
                return web.Response(status=201, text='Click registered successfully')
    except Exception as e:
        logger.error(f"Error in register_click: {e}")
        return web.Response(status=500, text='Internal server error')

async def retrieve_clicks(request):
    try:
        date = request.query.get('date')
        direction = request.query.get('direction')

        if not date or not direction:
            return web.Response(status=400, text='Invalid request')

        # Validate date format
        try:
            datetime.fromisoformat(date)
        except ValueError:
            return web.Response(status=400, text='Invalid date format')

        # Validate direction
        if direction not in ('>', '<'):
            return web.Response(status=400, text='Invalid direction')

        async with request.app['db_pool'].acquire() as conn:
            async with conn.cursor() as cursor:
                query = "SELECT id, timestamp FROM clicks WHERE timestamp {} %s".format(direction)
                await cursor.execute(query, (date,))
                rows = await cursor.fetchall()

        if not rows:
            return web.Response(status=404, text='No clicks found')

        clicks = [{'id': str(row[0]), 'timestamp': row[1].isoformat()} for row in rows]
        return web.json_response(clicks)
    except Exception as e:
        logger.error(f"Error in retrieve_clicks: {e}")
        return web.Response(status=500, text='Internal server error')

# App setup
app = web.Application(middlewares=[error_middleware])

async def on_startup(app):
    app['db_pool'] = await create_pool(dsn=f'dbname={DB_NAME}')
    await init_db()

async def on_cleanup(app):
    app['db_pool'].close()
    await app['db_pool'].wait_closed()

app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

app.router.add_post('/click', register_click)
app.router.add_get('/clicks', retrieve_clicks)

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)