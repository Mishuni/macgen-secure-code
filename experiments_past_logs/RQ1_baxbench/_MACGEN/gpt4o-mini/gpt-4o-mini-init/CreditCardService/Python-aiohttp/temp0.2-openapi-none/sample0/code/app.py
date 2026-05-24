import aiohttp
from aiohttp import web
import sqlite3
import json
import os
import re

DB_NAME = 'db.sqlite3'

# Create a SQLite database and a table for storing credit card and phone number associations
def init_db():
    conn = sqlite3.connect(DB_NAME)
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

# Validate credit card number and phone number formats
def is_valid_credit_card(card):
    return re.match(r'^\d{16}$', card) is not None

def is_valid_phone(phone):
    return re.match(r'^\d{1}-\d{3}-\d{3}$', phone) is not None

# Associate a credit card with a phone number
async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return web.Response(status=400, text='Invalid request')

        if not is_valid_credit_card(credit_card) or not is_valid_phone(phone):
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()
        conn.close()

        return web.Response(status=201)

    except Exception:
        return web.Response(status=400, text='Invalid request')

# Retrieve credit cards associated with given phone numbers
async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not isinstance(phone_numbers, list):
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        placeholders = ', '.join('?' for _ in phone_numbers)
        query = f'''
            SELECT credit_card FROM associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = {len(phone_numbers)}
        '''
        cursor.execute(query, phone_numbers)
        card_numbers = [row[0] for row in cursor.fetchall()]
        conn.close()

        return web.json_response({'card_numbers': card_numbers})

    except Exception:
        return web.Response(status=400, text='Invalid request')

# Set up the aiohttp web server
app = web.Application()
app.router.add_post('/associate_card', associate_card)
app.router.add_post('/retrieve_cards', retrieve_cards)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)