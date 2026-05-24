
import os
import sqlite3
from aiohttp import web
import json

DATABASE = 'db.sqlite3'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE, isolation_level=None)
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

# Handler for associating a credit card with a phone number
async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect(DATABASE, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO card_phone_association (credit_card, phone)
            VALUES (?, ?)
        ''', (credit_card, phone))
        conn.commit()
        conn.close()

        return web.Response(status=201, text='Association created successfully')
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Handler for retrieving credit cards associated with phone numbers
async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not isinstance(phone_numbers, list):
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect(DATABASE, isolation_level=None)
        cursor = conn.cursor()
        query = '''
            SELECT credit_card FROM card_phone_association
            WHERE phone IN ({})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        '''.format(','.join('?' for _ in phone_numbers))
        cursor.execute(query, phone_numbers + [len(phone_numbers)])
        rows = cursor.fetchall()
        conn.close()

        card_numbers = [row[0] for row in rows]
        if not card_numbers:
            return web.Response(status=404, text='Not found')

        return web.json_response({'card_numbers': card_numbers})
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Main function to set up the web server
def main():
    init_db()
    app = web.Application()
    app.router.add_post('/associate_card', associate_card)
    app.router.add_post('/retrieve_cards', retrieve_cards)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()