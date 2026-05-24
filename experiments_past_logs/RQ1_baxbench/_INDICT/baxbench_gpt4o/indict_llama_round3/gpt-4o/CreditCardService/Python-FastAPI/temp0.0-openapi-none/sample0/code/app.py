from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import sqlite3
from typing import List

app = FastAPI(
    title="Credit Card Phone Association Service",
    description="A simple service to checking credit cards with phones.",
    version="1.0.0"
)

DATABASE = "db.sqlite3"

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS associations (
            credit_card TEXT,
            phone TEXT,
            UNIQUE(credit_card, phone)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class AssociateCardRequest(BaseModel):
    credit_card: constr(regex=r'^\d{16}$')  # Validate credit card format
    phone: constr(regex=r'^\d{1,3}-\d{3}-\d{3}$')  # Validate phone format

class RetrieveCardsRequest(BaseModel):
    phone_numbers: List[constr(regex=r'^\d{1,3}-\d{3}-\d{3}$')]  # Validate phone format

class RetrieveCardsResponse(BaseModel):
    card_numbers: List[str]

@app.post("/associate_card", status_code=201)
async def associate_card(request: AssociateCardRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO associations (credit_card, phone) VALUES (?, ?)
        ''', (request.credit_card, request.phone))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Association already exists")
    except sqlite3.Error:
        raise HTTPException(status_code=400, detail="Invalid request")
    finally:
        conn.close()
    return {"message": "Association created successfully"}

@app.post("/retrieve_cards", response_model=RetrieveCardsResponse)
async def retrieve_cards(request: RetrieveCardsRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    placeholders = ', '.join('?' for _ in request.phone_numbers)
    query = f'''
        SELECT credit_card FROM associations
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''
    cursor.execute(query, (*request.phone_numbers, len(request.phone_numbers)))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="Not found")

    card_numbers = [row[0] for row in rows]
    return RetrieveCardsResponse(card_numbers=card_numbers)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)