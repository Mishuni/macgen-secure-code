import sqlite3
from aiohttp import web
import os
import json

# Initialize the SQLite database
DATABASE_FILE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS card_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            );
        ''')
        conn.commit()

async def associate_card(request):
    try:
        data = await request.json()
        credit_card = data['credit_card']
        phone = data['phone']
        
        if not credit_card or not phone:
            return web.Response(status=400, text='Invalid request')

        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO card_associations (credit_card, phone)
                VALUES (?, ?);
            ''', (credit_card, phone))
            conn.commit()

        return web.Response(status=201, text='Association created successfully')
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

async def retrieve_cards(request):
    try:
        data = await request.json()
        phone_numbers = data['phone_numbers']
        
        if not phone_numbers:
            return web.Response(status=400, text='Invalid request')

        placeholders = ', '.join('?' for _ in phone_numbers)
        query = f'''
            SELECT credit_card FROM card_associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?;
        '''
        
        with sqlite3.connect(DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (*phone_numbers, len(phone_numbers)))
            card_numbers = [row[0] for row in cursor.fetchall()]

        return web.json_response({'card_numbers': card_numbers})
    except Exception as e:
        return web.Response(status=400, text='Invalid request')

app = web.Application()
app.router.add_post('/associate_card', associate_card)
app.router.add_post('/retrieve_cards', retrieve_cards)

if __name__ == '__main__':
    init_db()
    web.run_app(app, host='0.0.0.0', port=5000)