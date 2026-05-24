from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import sqlite3
import os

app = FastAPI()

# Database setup
DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS associations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_card TEXT NOT NULL,
                phone TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

class AssociateCardRequest(BaseModel):
    credit_card: constr(regex=r'^\d{16}$')  # 16 digits
    phone: constr(regex=r'^\d{1}-\d{3}-\d{3}$')  # Format: 1-100-111

class RetrieveCardsRequest(BaseModel):
    phone_numbers: list[constr(regex=r'^\d{1}-\d{3}-\d{3}$')]  # Format: 1-100-111

class RetrieveCardsResponse(BaseModel):
    card_numbers: list[str]

@app.post("/associate_card", status_code=201)
async def associate_card(request: AssociateCardRequest):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO associations (credit_card, phone) VALUES (?, ?)
            ''', (request.credit_card, request.phone))
            conn.commit()
        except sqlite3.Error:
            raise HTTPException(status_code=400, detail="Invalid request")

@app.post("/retrieve_cards", response_model=RetrieveCardsResponse)
async def retrieve_cards(request: RetrieveCardsRequest):
    if not request.phone_numbers:
        raise HTTPException(status_code=400, detail="Invalid request")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        placeholders = ', '.join('?' for _ in request.phone_numbers)
        query = f'''
            SELECT credit_card FROM associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = {len(request.phone_numbers)}
        '''
        cursor.execute(query, request.phone_numbers)
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="Not found")

        card_numbers = [row[0] for row in rows]
        return RetrieveCardsResponse(card_numbers=card_numbers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)