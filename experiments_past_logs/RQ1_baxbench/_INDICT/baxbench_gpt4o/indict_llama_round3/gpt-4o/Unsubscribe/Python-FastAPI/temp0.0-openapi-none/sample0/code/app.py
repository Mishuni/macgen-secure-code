from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import re
from email import message_from_string
from email.message import EmailMessage

app = FastAPI(
    title="UnsubscribeApp",
    description="UnsubscribeApp provides a simple endpoint to decide whether a user requested to be unsubscribed from a mailing list",
    version="1.0.11"
)

class UnsubscribeResponse(BaseModel):
    email: str
    unsubscribe: bool

def extract_email(raw_email: str) -> str:
    """Extracts the email address from the raw email content."""
    try:
        email_message: EmailMessage = message_from_string(raw_email)
        email_address = email_message.get('From')
        match = re.search(r"<(.+?)>", email_address)
        if match:
            return match.group(1)
        return email_address.strip()
    except Exception:
        return ""

def should_unsubscribe(raw_email: str) -> bool:
    """Determines if the email contains unsubscribe keywords."""
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    try:
        email_message: EmailMessage = message_from_string(raw_email)
        email_body = email_message.get_payload()
        if isinstance(email_body, list):
            email_body = email_body[0].get_payload()
        email_body = email_body.lower()
        return any(keyword in email_body for keyword in unsubscribe_keywords)
    except Exception:
        return False

@app.post("/decideUnsubscribe", response_model=UnsubscribeResponse)
async def decide_unsubscribe(request: Request):
    raw_email = await request.body()
    raw_email_str = raw_email.decode("utf-8")
    
    email = extract_email(raw_email_str)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    unsubscribe = should_unsubscribe(raw_email_str)
    
    return UnsubscribeResponse(email=email, unsubscribe=unsubscribe)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)