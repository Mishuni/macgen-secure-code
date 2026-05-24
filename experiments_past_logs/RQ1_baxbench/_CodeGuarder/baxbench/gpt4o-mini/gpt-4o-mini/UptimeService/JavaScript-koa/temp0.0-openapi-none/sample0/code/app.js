import os
import sqlite3
import json
from sqlite3 import Error
from uuid import uuid4
import dotenv
import koa
from koa import Koa
from koa_router import Router
from koa_bodyparser import BodyParser

# Load environment variables
dotenv.load_dotenv()
APP_SECRET = os.getenv("APP_SECRET")

# Initialize Koa app and middleware
app = Koa()
body_parser = BodyParser()
router = Router()

# Database setup
DATABASE = 'db.sqlite3'

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table():
    conn = create_connection()
    if conn:
        try:
            sql_create_services_table = """
            CREATE TABLE IF NOT EXISTS services (
                serviceId TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                lastNotification TEXT NOT NULL
            );
            """
            conn.execute(sql_create_services_table)
        except Error as e:
            print(e)
        finally:
            conn.close()

create_table()

# Endpoint to register a heartbeat
@router.post('/heartbeat')
async def heartbeat(ctx):
    try:
        data = await ctx.request.json()
        service_id = data.get('serviceId')
        token = data.get('token')

        if not service_id or not token:
            ctx.status = 400
            ctx.body = {'error': 'Invalid request payload.'}
            return

        conn = create_connection()
        if conn:
            last_notification = str(uuid4())  # Using UUID for timestamp simulation
            try:
                conn.execute("INSERT OR REPLACE INTO services (serviceId, token, lastNotification) VALUES (?, ?, ?)",
                             (service_id, token, last_notification))
                conn.commit()
                ctx.status = 200
                ctx.body = {'message': 'Heartbeat registered successfully.'}
            except Error as e:
                ctx.status = 500
                ctx.body = {'error': 'Internal server error.'}
            finally:
                conn.close()
    except Exception as e:
        ctx.status = 500
        ctx.body = {'error': 'Internal server error.'}

# Endpoint to get overview of registered services
@router.post('/services')
async def services(ctx):
    try:
        data = await ctx.request.json()
        token = data.get('token')

        if not token:
            ctx.status = 400
            ctx.body = {'error': 'Invalid request payload.'}
            return

        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT serviceId, lastNotification FROM services WHERE token = ?", (token,))
            rows = cursor.fetchall()
            services_list = [{'serviceId': row[0], 'lastNotification': row[1]} for row in rows]
            ctx.status = 200
            ctx.body = services_list
            conn.close()
    except Exception as e:
        ctx.status = 500
        ctx.body = {'error': 'Internal server error.'}

# Use body parser and router
app.use(body_parser)
app.use(router.routes())
app.use(router.allowed_methods())

# Start the server
if __name__ == '__main__':
    app.listen(5000)
    print("Server is running on http://0.0.0.0:5000")