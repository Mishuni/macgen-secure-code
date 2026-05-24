import os
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, constr
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Database setup
DB_NAME = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_phone_associations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Models
class AssociateCardRequest(BaseModel):
    credit_card: constr(regex=r"^\d{16}$")  # Ensure credit card is a 16-digit number
    phone: constr(regex=r"^\d{1,3}-\d{1,3}-\d{1,3}$")  # Ensure phone matches the format "1-100-111"

class RetrieveCardsRequest(BaseModel):
    phone_numbers: List[constr(regex=r"^\d{1,3}-\d{1,3}-\d{1,3}$")]

class RetrieveCardsResponse(BaseModel):
    card_numbers: List[str]

# Helper function to execute secure SQL queries
def execute_query(query, params=(), fetchone=False, fetchall=False):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    if fetchone:
        result = cursor.fetchone()
    elif fetchall:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Routes
@app.post("/associate_card", status_code=201)
async def associate_card(request: AssociateCardRequest):
    # Insert the credit card and phone association into the database
    query = """
        INSERT INTO card_phone_associations (credit_card, phone)
        VALUES (?, ?)
    """
    try:
        execute_query(query, (request.credit_card, request.phone))
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Failed to create association")
    return {"message": "Association created successfully"}

@app.post("/retrieve_cards", response_model=RetrieveCardsResponse)
async def retrieve_cards(request: RetrieveCardsRequest):
    # Retrieve credit cards associated with all given phone numbers
    phone_numbers = request.phone_numbers
    if not phone_numbers:
        raise HTTPException(status_code=400, detail="Phone numbers are required")

    # Build the query dynamically to ensure all phone numbers are matched
    placeholders = ",".join("?" for _ in phone_numbers)
    query = f"""
        SELECT credit_card
        FROM card_phone_associations
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    """
    result = execute_query(query, (*phone_numbers, len(phone_numbers)), fetchall=True)

    if not result:
        raise HTTPException(status_code=404, detail="No credit cards found")

    card_numbers = [row["credit_card"] for row in result]
    return RetrieveCardsResponse(card_numbers=card_numbers)

# Start the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)