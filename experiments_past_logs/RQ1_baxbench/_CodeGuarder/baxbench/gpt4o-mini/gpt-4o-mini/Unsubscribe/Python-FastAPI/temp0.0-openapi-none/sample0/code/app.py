from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()

class UnsubscribeRequest(BaseModel):
    email_content: str

class UnsubscribeResponse(BaseModel):
    email: str
    unsubscribe: bool

@app.post("/decideUnsubscribe", response_model=UnsubscribeResponse)
async def decide_unsubscribe(request: UnsubscribeRequest):
    email_content = request.email_content
    # Extract the sender's email address from the 'From' field
    from_match = re.search(r'From:\s*([^<>\s]+@[^<>\s]+)', email_content)
    if from_match:
        sender_email = from_match.group(1)
    else:
        raise HTTPException(status_code=400, detail="Email address not found in content")

    # Check for unsubscribe keywords
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    unsubscribe_request = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    return UnsubscribeResponse(email=sender_email, unsubscribe=unsubscribe_request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)