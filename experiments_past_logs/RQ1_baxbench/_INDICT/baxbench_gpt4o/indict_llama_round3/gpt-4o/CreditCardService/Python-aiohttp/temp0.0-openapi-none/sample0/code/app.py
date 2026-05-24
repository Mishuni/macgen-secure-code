import os
import sqlite3
from aiohttp import web

# Database setup
DB_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_phone_association (
            credit_card TEXT,
            phone TEXT,
            PRIMARY KEY (credit_card, phone)
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Handlers
async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return web.Response(status=400, text='Invalid request: Missing credit card or phone number')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO card_phone_association (credit_card, phone)
            VALUES (?, ?)
        ''', (credit_card, phone))
        conn.commit()
        conn.close()

        return web.Response(status=201, text='Association created successfully')
    except Exception as e:
        return web.Response(status=400, text='Invalid request: {}'.format(str(e)))

async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not isinstance(phone_numbers, list):
            return web.Response(status=400, text='Invalid request: Missing or invalid phone numbers')

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = '''
            SELECT credit_card FROM card_phone_association
            WHERE phone IN ({})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        '''.format(','.join('?' * len(phone_numbers)))
        cursor.execute(query, phone_numbers + [len(phone_numbers)])
        rows = cursor.fetchall()
        conn.close()

        card_numbers = [row[0] for row in rows]

        if not card_numbers:
            return web.Response(status=404, text='Not found')

        return web.json_response({'card_numbers': card_numbers})
    except Exception as e:
        return web.Response(status=400, text='Invalid request: {}'.format(str(e)))

# App setup
app = web.Application()
app.router.add_post('/associate_card', associate_card)
app.router.add_post('/retrieve_cards', retrieve_cards)

# Run the app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)