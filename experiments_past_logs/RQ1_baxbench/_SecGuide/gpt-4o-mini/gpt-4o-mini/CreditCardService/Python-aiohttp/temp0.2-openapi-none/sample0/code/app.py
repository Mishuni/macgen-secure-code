import aiohttp
from aiohttp import web
import sqlite3
import os
import json
import re

# Initialize SQLite database
def init_db():
    db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')  # Use environment variable for database path
    conn = sqlite3.connect(db_path)
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
    credit_card_pattern = r'^\d{16}$'  # Example pattern for a 16-digit credit card
    phone_pattern = r'^\+?\d{10,15}$'  # Example pattern for international phone numbers
    return re.match(credit_card_pattern, credit_card) and re.match(phone_pattern, phone)

# Create a new association of a credit card number with a phone number
async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data['credit_card']
        phone = data['phone']
        
        if not credit_card or not phone or not validate_input(credit_card, phone):
            return web.Response(status=400, text='Invalid request')

        db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()
        conn.close()

        return web.Response(status=201)
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid request')
    except sqlite3.Error as e:
        return web.Response(status=500, text='Database error')

# Retrieve cards associated with a set of phone numbers
async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data['phone_numbers']

        if not phone_numbers or not all(validate_input('', phone) for phone in phone_numbers):
            return web.Response(status=400, text='Invalid request')

        db_path = os.getenv('DATABASE_PATH', 'db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in phone_numbers)
        query = f'SELECT DISTINCT credit_card FROM associations WHERE phone IN ({placeholders}) GROUP BY credit_card HAVING COUNT(DISTINCT phone) = ?'
        cursor.execute(query, (*phone_numbers, len(phone_numbers)))
        card_numbers = [row[0] for row in cursor.fetchall()]
        conn.close()

        if card_numbers:
            return web.json_response({'card_numbers': card_numbers})
        else:
            return web.Response(status=404, text='Not found')
    except (KeyError, json.JSONDecodeError):
        return web.Response(status=400, text='Invalid request')
    except sqlite3.Error as e:
        return web.Response(status=500, text='Database error')

# Create the web application
app = web.Application()
app.router.add_post('/associate_card', associate_card)
app.router.add_post('/retrieve_cards', retrieve_cards)

# Initialize the database and start the server
if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)