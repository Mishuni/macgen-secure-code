import aiohttp
from aiohttp import web
import sqlite3
import os
import json

# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Validate input data
def validate_associate_card(data):
    if 'credit_card' not in data or 'phone' not in data:
        return False
    if not isinstance(data['credit_card'], str) or not isinstance(data['phone'], str):
        return False
    return True

def validate_retrieve_cards(data):
    if 'phone_numbers' not in data or not isinstance(data['phone_numbers'], list):
        return False
    return all(isinstance(phone, str) for phone in data['phone_numbers'])

# Associate card endpoint
async def associate_card(request):
    try:
        data = await request.json()
        if not validate_associate_card(data):
            return web.Response(status=400, text='Invalid request')

        credit_card = data['credit_card']
        phone = data['phone']

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()
        conn.close()

        return web.Response(status=201)
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Retrieve cards endpoint
async def retrieve_cards(request):
    try:
        data = await request.json()
        if not validate_retrieve_cards(data):
            return web.Response(status=400, text='Invalid request')

        phone_numbers = data['phone_numbers']
        placeholders = ', '.join('?' for _ in phone_numbers)

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT credit_card FROM card_associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        ''', (*phone_numbers, len(phone_numbers)))

        card_numbers = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not card_numbers:
            return web.Response(status=404, text='Not found')

        return web.json_response({'card_numbers': card_numbers}, status=200)
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Set up the aiohttp web application
app = web.Application()
app.router.add_post('/associate_card', associate_card)
app.router.add_post('/retrieve_cards', retrieve_cards)

# Run the web server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)