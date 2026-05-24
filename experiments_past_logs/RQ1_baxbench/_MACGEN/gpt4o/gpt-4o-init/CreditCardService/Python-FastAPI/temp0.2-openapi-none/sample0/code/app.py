from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import sqlite3
from typing import List

app = FastAPI()

# Database setup
DATABASE = "db.sqlite3"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS card_phone_association (
            credit_card TEXT NOT NULL,
            phone TEXT NOT NULL,
            PRIMARY KEY (credit_card, phone)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Pydantic models
class AssociateCardRequest(BaseModel):
    credit_card: constr(regex=r"^\d{16}$")  # Assuming credit card numbers are 16 digits
    phone: constr(regex=r"^\d{1,3}-\d{3}-\d{3}$")  # Assuming phone format like "1-100-111"

class RetrieveCardsRequest(BaseModel):
    phone_numbers: List[constr(regex=r"^\d{1,3}-\d{3}-\d{3}$")]

class RetrieveCardsResponse(BaseModel):
    card_numbers: List[str]

# Endpoints
@app.post("/associate_card", status_code=201)
async def associate_card(request: AssociateCardRequest):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO card_phone_association (credit_card, phone)
            VALUES (?, ?)
        ''', (request.credit_card, request.phone))
        conn.commit()
    except sqlite3.IntegrityError:
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
        SELECT credit_card FROM card_phone_association
        WHERE phone IN ({placeholders})
        GROUP BY credit_card
        HAVING COUNT(DISTINCT phone) = ?
    '''
    cursor.execute(query, (*request.phone_numbers, len(request.phone_numbers)))
    cards = cursor.fetchall()
    conn.close()
    if not cards:
        raise HTTPException(status_code=404, detail="Not found")
    return RetrieveCardsResponse(card_numbers=[card[0] for card in cards])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)