import os
import sqlite3
from aiohttp import web
import json
import re

# Database setup
DB_NAME = os.getenv('DB_NAME', 'db.sqlite3')

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_phone_association (
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL,
            PRIMARY KEY (credit_card, phone)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Helper function to validate credit card and phone number
def validate_credit_card(card_number):
    # Implementing Luhn's algorithm for validation
    def luhn_checksum(card_number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10

    return card_number.isdigit() and len(card_number) == 16 and luhn_checksum(card_number) == 0

def validate_phone_number(phone_number):
    # Enforcing a stricter phone number format
    return re.match(r'^\+?\d{10,15}$', phone_number) is not None

# Handler for associating a credit card with a phone number
async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return web.Response(status=400, text='Invalid request: Missing credit card or phone number')

        if not validate_credit_card(credit_card) or not validate_phone_number(phone):
            return web.Response(status=400, text='Invalid request: Invalid credit card or phone number format')

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO card_phone_association (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
            conn.commit()
        except sqlite3.IntegrityError:
            return web.Response(status=400, text='Association already exists')
        except sqlite3.Error:
            return web.Response(status=500, text='Internal server error')
        finally:
            conn.close()

        return web.Response(status=201, text='Association created successfully')
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid request: JSON decode error')

# Handler for retrieving credit cards associated with phone numbers
async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not all(validate_phone_number(phone) for phone in phone_numbers):
            return web.Response(status=400, text='Invalid request: Invalid phone numbers format')

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            query = '''
                SELECT credit_card FROM card_phone_association
                WHERE phone IN ({})
                GROUP BY credit_card
                HAVING COUNT(DISTINCT phone) = ?
            '''.format(','.join('?' for _ in phone_numbers))
            cursor.execute(query, phone_numbers + [len(phone_numbers)])
            cards = [row[0] for row in cursor.fetchall()]
        except sqlite3.Error:
            return web.Response(status=500, text='Internal server error')
        finally:
            conn.close()

        if not cards:
            return web.Response(status=404, text='Not found')

        return web.json_response({'card_numbers': cards})
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid request: JSON decode error')

# Create the web application
app = web.Application()

# Add routes
app.router.add_post('/associate_card', associate_card)
app.router.add_post('/retrieve_cards', retrieve_cards)

# Run the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)