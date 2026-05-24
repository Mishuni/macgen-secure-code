import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, validator
from typing import List
import re

# Initialize FastAPI app
app = FastAPI(
    title="Credit Card Phone Association Service",
    description="A simple service to check credit cards with phones.",
    version="1.0.0"
)

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_phone_association (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class AssociateCardRequest(BaseModel):
    credit_card: str
    phone: str

    @validator('credit_card')
    def validate_credit_card(cls, v):
        # Simple Luhn check for credit card validation
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

        if not v.isdigit() or luhn_checksum(v) != 0:
            raise ValueError('Invalid credit card number')
        return v

    @validator('phone')
    def validate_phone(cls, v):
        if not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

class RetrieveCardsRequest(BaseModel):
    phone_numbers: List[str]

    @validator('phone_numbers', each_item=True)
    def validate_phone_numbers(cls, v):
        if not re.match(r'^\+?[1-9]\d{1,14}$', v):
            raise ValueError('Invalid phone number format')
        return v

# Helper function to execute queries
def execute_query(query, params=()):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_query(query, params=()):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

# API endpoints
@app.post("/associate_card", status_code=201)
async def associate_card(request: AssociateCardRequest):
    try:
        execute_query(
            "INSERT INTO card_phone_association (credit_card, phone) VALUES (?, ?)",
            (request.credit_card, request.phone)
        )
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail="Database error")
    return {"message": "Association created successfully"}

@app.post("/retrieve_cards", status_code=200)
async def retrieve_cards(request: RetrieveCardsRequest):
    try:
        placeholders = ', '.join('?' for _ in request.phone_numbers)
        query = '''
            SELECT credit_card FROM card_phone_association
            WHERE phone IN ({})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        '''.format(placeholders)
        result = fetch_query(query, (*request.phone_numbers, len(request.phone_numbers)))
        card_numbers = [row[0] for row in result]
        if not card_numbers:
            raise HTTPException(status_code=404, detail="Not found")
        return {"card_numbers": card_numbers}
    except sqlite3.Error as e:
        raise HTTPException(status_code=400, detail="Database error")

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)