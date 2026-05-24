
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import uvicorn
import email
from email import policy
from email.parser import BytesParser
from email_validator import validate_email, EmailNotValidError

app = FastAPI()

class UnsubscribeResponse(BaseModel):
    email: str
    unsubscribe: bool

@app.post("/decideUnsubscribe", response_model=UnsubscribeResponse)
async def decide_unsubscribe(request: Request):
    try:
        raw_email = await request.body()
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)
        
        # Extract and validate the 'From' email address
        from_email = msg['From']
        try:
            valid = validate_email(from_email)
            from_email = valid.email
        except EmailNotValidError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Extract the email body
        email_body = msg.get_body(preferencelist=('plain')).get_content()

        # Define keywords for unsubscribe requests
        unsubscribe_keywords = [
            "unsubscribe", "remove me", "deregister me", 
            "stop sending me", "delete me"
        ]

        # Check for unsubscribe keywords in the email body
        unsubscribe_decision = any(keyword in email_body.lower() for keyword in unsubscribe_keywords)

        return UnsubscribeResponse(email=from_email, unsubscribe=unsubscribe_decision)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid email format")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)