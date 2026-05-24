from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr, validator
import sqlite3
import os
import re

app = FastAPI()

# Database setup
DATABASE = os.getenv('DATABASE_PATH', 'db.sqlite3')

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

class CardAssociation(BaseModel):
    credit_card: constr(regex=r'^\d{16}$')  # Ensures credit card is exactly 16 digits
    phone: constr(min_length=10)  # Basic validation for phone number length

    @validator('credit_card')
    def validate_credit_card(cls, v):
        if not re.match(r'^\d{16}$', v):
            raise ValueError('Invalid credit card number format')
        # Implement Luhn's algorithm check here if needed
        return v

class PhoneNumbers(BaseModel):
    phone_numbers: list[constr(min_length=10)]  # Basic validation for phone number length

@app.post("/associate_card", status_code=201)
async def associate_card(association: CardAssociation):
    if not association.phone:
        raise HTTPException(status_code=400, detail="Invalid phone number")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO associations (credit_card, phone) VALUES (?, ?)
        ''', (association.credit_card, association.phone))
        conn.commit()

    return {"message": "Association created successfully"}

@app.post("/retrieve_cards", response_model=dict)
async def retrieve_cards(phone_numbers: PhoneNumbers):
    if not phone_numbers.phone_numbers:
        raise HTTPException(status_code=400, detail="Invalid request")

    placeholders = ', '.join('?' for _ in phone_numbers.phone_numbers)
    query = f'''
        SELECT credit_card FROM associations
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = {len(phone_numbers.phone_numbers)}
    '''

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, phone_numbers.phone_numbers)
        results = cursor.fetchall()

    if not results:
        raise HTTPException(status_code=404, detail="Not found")

    # Masking credit card numbers before sending them back
    card_numbers = [f"**** **** **** {row[0][-4:]}" for row in results]
    return {"card_numbers": card_numbers}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)