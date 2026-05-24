import os
import sqlite3
from aiohttp import web
import json

# Database setup
DATABASE_NAME = 'db.sqlite3'

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
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

# Helper function to get environment variable safely
def get_env_variable(name, default=None):
    try:
        return os.environ[name]
    except KeyError:
        if default is not None:
            return default
        raise EnvironmentError(f"Set the {name} environment variable")

# Endpoint to associate a credit card with a phone number
async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data.get('credit_card')
        phone = data.get('phone')

        if not credit_card or not phone:
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()
        conn.close()

        return web.Response(status=201, text='Association created successfully')
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Endpoint to retrieve cards associated with a set of phone numbers
async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data.get('phone_numbers')

        if not phone_numbers or not isinstance(phone_numbers, list):
            return web.Response(status=400, text='Invalid request')

        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        query = '''
            SELECT credit_card FROM card_associations
            WHERE phone IN ({seq})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        '''.format(seq=','.join(['?']*len(phone_numbers)))
        cursor.execute(query, phone_numbers + [len(phone_numbers)])
        rows = cursor.fetchall()
        conn.close()

        card_numbers = [row[0] for row in rows]
        if not card_numbers:
            return web.Response(status=404, text='Not found')

        return web.json_response({'card_numbers': card_numbers})
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

# Main application setup
def create_app():
    app = web.Application()
    app.router.add_post('/associate_card', associate_card)
    app.router.add_post('/retrieve_cards', retrieve_cards)
    return app

if __name__ == '__main__':
    init_db()
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=5000)