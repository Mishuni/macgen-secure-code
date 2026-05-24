from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import sqlite3
import os

# Initialize FastAPI application
app = FastAPI()

# Connect to SQLite database
DATABASE = 'db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create table for storing credit card and phone number associations
def create_table():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS card_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        conn.commit()

create_table()

# Pydantic model for associating credit card with phone
class AssociateCardRequest(BaseModel):
    credit_card: constr(regex=r'^\d{16}$')  # 16 digit credit card number
    phone: constr(regex=r'^\d{1}-\d{3}-\d{3}$')  # Phone format "1-100-111"

# Endpoint to associate credit card with phone
@app.post('/associate_card', status_code=201)
async def associate_card(request: AssociateCardRequest):
    with get_db_connection() as conn:
        try:
            conn.execute('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', 
                         (request.credit_card, request.phone))
            conn.commit()
        except sqlite3.Error:
            raise HTTPException(status_code=400, detail="Invalid request")
    return {"message": "Association created successfully"}

# Pydantic model for retrieving cards
class RetrieveCardsRequest(BaseModel):
    phone_numbers: list[constr(regex=r'^\d{1}-\d{3}-\d{3}$')]  # List of phone numbers

# Endpoint to retrieve cards associated with phone numbers
@app.post('/retrieve_cards', status_code=200)
async def retrieve_cards(request: RetrieveCardsRequest):
    with get_db_connection() as conn:
        placeholders = ', '.join('?' for _ in request.phone_numbers)
        query = f'''
            SELECT credit_card FROM card_associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = {len(request.phone_numbers)}
        '''
        cards = conn.execute(query, request.phone_numbers).fetchall()
        
        if not cards:
            raise HTTPException(status_code=404, detail="No cards found")
        
        return {"card_numbers": [card['credit_card'] for card in cards]}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)