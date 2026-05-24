import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

# Initialize FastAPI
app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

# Create tables if they do not exist
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS card_associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        conn.commit()

# Pydantic models for request bodies
class AssociateCardRequest(BaseModel):
    credit_card: str
    phone: str

class RetrieveCardsRequest(BaseModel):
    phone_numbers: list[str]

class RetrieveCardsResponse(BaseModel):
    card_numbers: list[str]

# Initialize the database
init_db()

@app.post("/associate_card", status_code=201)
async def associate_card(request: AssociateCardRequest):
    credit_card = request.credit_card
    phone = request.phone

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)', (credit_card, phone))
        conn.commit()

    return {"message": "Association created successfully"}

@app.post("/retrieve_cards", response_model=RetrieveCardsResponse)
async def retrieve_cards(request: RetrieveCardsRequest):
    phone_numbers = request.phone_numbers

    if not phone_numbers:
        raise HTTPException(status_code=400, detail="Invalid request")

    placeholders = ', '.join('?' for _ in phone_numbers)
    query = f'''
        SELECT credit_card FROM card_associations
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, (*phone_numbers, len(phone_numbers)))
        results = cursor.fetchall()

    card_numbers = [row[0] for row in results]

    if not card_numbers:
        raise HTTPException(status_code=404, detail="Not found")

    return RetrieveCardsResponse(card_numbers=card_numbers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)