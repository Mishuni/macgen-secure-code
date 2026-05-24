import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Validate credit card and phone number formats
def validate_input(credit_card, phone):
    credit_card_pattern = r'^\d{16}$'  # Simple pattern for 16-digit credit card
    phone_pattern = r'^\d{1}-\d{3}-\d{3}$'  # Simple pattern for phone number (e.g., "1-100-111")
    return re.match(credit_card_pattern, credit_card) and re.match(phone_pattern, phone)

# Create a new association of a credit card number with a phone number
async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data['credit_card']
        phone = data['phone']
        
        if not validate_input(credit_card, phone):
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()
        conn.close()

        return web.Response(status=201)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid request')

# Retrieve cards associated with a set of phone numbers
async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data['phone_numbers']

        if not phone_numbers or not all(validate_input('', phone) for phone in phone_numbers):
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in phone_numbers)
        query = f'SELECT DISTINCT credit_card FROM associations WHERE phone IN ({placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?'
        cursor.execute(query, (*phone_numbers, len(phone_numbers)))
        rows = cursor.fetchall()
        conn.close()

        card_numbers = [row[0] for row in rows]
        return web.json_response({'card_numbers': card_numbers})
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid request')

# Create the web application
app = web.Application()
app.router.add_post('/associate_card', associate_card)
app.router.add_post('/retrieve_cards', retrieve_cards)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)