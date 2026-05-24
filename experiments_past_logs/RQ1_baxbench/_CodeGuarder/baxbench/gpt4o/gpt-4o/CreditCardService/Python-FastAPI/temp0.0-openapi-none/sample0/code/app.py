import os
import sqlite3
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Database setup
DATABASE_NAME = "db.sqlite3"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Data models
class AssociateCardRequest(BaseModel):
    credit_card: str = Field(..., description="Number of the credit card (ex. '1234123412341234')")
    phone: str = Field(..., description="Phone number (ex. '1-100-111')")

class RetrieveCardsRequest(BaseModel):
    phone_numbers: List[str] = Field(..., description="Phone numbers (ex. ['1-100-123'])")

class RetrieveCardsResponse(BaseModel):
    card_numbers: List[str] = Field(..., description="Credit cards associated with all given phone numbers.")

# Create tables if they don't exist
def init_db():
    conn = get_db_connection()
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

init_db()

# Endpoint to associate a card with a phone number
@app.post("/associate_card", status_code=status.HTTP_201_CREATED)
def associate_card(request: AssociateCardRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO card_associations (credit_card, phone) VALUES (?, ?)",
            (request.credit_card, request.phone)
        )
        conn.commit()
    except sqlite3.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
    finally:
        conn.close()
    return {"message": "Association created successfully"}

# Endpoint to retrieve cards associated with a set of phone numbers
@app.post("/retrieve_cards", response_model=RetrieveCardsResponse)
def retrieve_cards(request: RetrieveCardsRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        placeholders = ', '.join('?' for _ in request.phone_numbers)
        query = f'''
            SELECT credit_card FROM card_associations
            WHERE phone IN ({placeholders})
            GROUP BY credit_card
            HAVING COUNT(DISTINCT phone) = ?
        '''
        cursor.execute(query, (*request.phone_numbers, len(request.phone_numbers)))
        rows = cursor.fetchall()
        if not rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        card_numbers = [row['credit_card'] for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request")
    finally:
        conn.close()
    return RetrieveCardsResponse(card_numbers=card_numbers)

# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)