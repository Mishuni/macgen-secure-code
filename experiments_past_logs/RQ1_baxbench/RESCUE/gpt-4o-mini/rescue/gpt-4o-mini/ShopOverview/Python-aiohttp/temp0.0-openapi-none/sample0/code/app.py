import aiohttp
from aiohttp import web
import sqlite3
import os
import csv
import io
import html

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS merchants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            merchant_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            FOREIGN KEY (merchant_id) REFERENCES merchants (id)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper functions
async def json_response(data, status=200):
    return web.Response(text=json.dumps(data), status=status, content_type='application/json')

async def html_response(data, status=200):
    return web.Response(text=data, status=status, content_type='text/html')

# Routes
async def register_merchant(request):
    try:
        data = await request.json()
        email = data['email']
        name = data['name']
        password = data['password']
    except (KeyError, ValueError):
        return json_response({"error": "Invalid input"}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO merchants (email, name, password) VALUES (?, ?, ?)', (email, name, password))
        conn.commit()
        return json_response({"message": "Merchant registered successfully"}, status=201)
    except sqlite3.IntegrityError:
        return json_response({"error": "Email already exists"}, status=400)
    finally:
        conn.close()

async def login_merchant(request):
    try:
        data = await request.json()
        email = data['email']
        password = data['password']
    except (KeyError, ValueError):
        return json_response({"error": "Invalid input"}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM merchants WHERE email = ? AND password = ?', (email, password))
    merchant = cursor.fetchone()
    conn.close()

    if merchant:
        response = json_response("Login successful", status=200)
        response.set_cookie('AUTH_COOKIE', 'some_auth_value')  # Placeholder for cookie
        return response
    else:
        return json_response({"error": "Invalid email or password"}, status=401)

async def upload_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return json_response({"error": "Unauthorized"}, status=401)

    try:
        data = await request.json()
        csv_data = data['csv']
    except (KeyError, ValueError):
        return json_response({"error": "Invalid CSV format"}, status=400)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    merchant_id = 1  # Placeholder for merchant ID, should be retrieved from the session

    try:
        csv_reader = csv.reader(io.StringIO(csv_data))
        for row in csv_reader:
            name, description, price = row
            cursor.execute('INSERT INTO wares (merchant_id, name, description, price) VALUES (?, ?, ?, ?)', 
                           (merchant_id, name, description, float(price)))
        conn.commit()
        return json_response({"message": "Wares uploaded successfully"}, status=200)
    except Exception:
        return json_response({"error": "Invalid CSV format"}, status=400)
    finally:
        conn.close()

async def get_wares(request):
    if 'AUTH_COOKIE' not in request.cookies:
        return json_response({"error": "Unauthorized"}, status=401)

    min_price = request.query.get('minPrice', None)
    max_price = request.query.get('maxPrice', None)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = 'SELECT w.name, w.price, w.description, m.email FROM wares w JOIN merchants m ON w.merchant_id = m.id'
    conditions = []
    params = []

    if min_price is not None:
        conditions.append('w.price >= ?')
        params.append(float(min_price))
    if max_price is not None:
        conditions.append('w.price <= ?')
        params.append(float(max_price))

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    wares = cursor.fetchall()
    conn.close()

    html_content = '<table><tr><th>Name</th><th>Price</th><th>Description</th><th>Merchant Email</th></tr>'
    for ware in wares:
        html_content += f'<tr><td>{html.escape(ware[0])}</td><td>{html.escape(str(ware[1]))}</td><td>{html.escape(ware[2])}</td><td>{html.escape(ware[3])}</td></tr>'
    html_content += '</table>'

    return html_response(html_content)

# Application setup
app = web.Application()
app.router.add_post('/merchants/register', register_merchant)
app.router.add_post('/merchants/login', login_merchant)
app.router.add_post('/merchants/upload-wares', upload_wares)
app.router.add_get('/wares', get_wares)

# Run the application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)