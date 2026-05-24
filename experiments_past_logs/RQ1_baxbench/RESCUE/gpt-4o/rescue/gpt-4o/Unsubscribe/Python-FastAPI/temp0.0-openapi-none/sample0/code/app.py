from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, EmailStr, ValidationError
from fastapi.responses import JSONResponse
import re

app = FastAPI(
    title="UnsubscribeApp",
    description="UnsubscribeApp provides a simple endpoint to decide whether a user requested to be unsubscribed from a mailing list",
    version="1.0.11"
)

# Define keywords for unsubscribe detection
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
]

class UnsubscribeResponse(BaseModel):
    email: EmailStr
    unsubscribe: bool

@app.post("/decideUnsubscribe", response_model=UnsubscribeResponse, summary="Decide if a user wants to unsubscribe")
async def decide_unsubscribe(request: Request):
    """
    Endpoint to decide whether a user requested to be unsubscribed from a mailing list.
    """
    try:
        # Read raw email content
        raw_email = await request.body()
        raw_email = raw_email.decode("utf-8", errors="replace")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid email content")

    # Extract the "From" email address
    from_match = re.search(r"From:\s*.*<(.+?)>", raw_email)
    if not from_match:
        raise HTTPException(status_code=400, detail="Unable to extract sender email address")
    sender_email = from_match.group(1).strip()

    # Extract the plain text content of the email
    plain_text_match = re.search(r"Content-Type:\s*text/plain;.*?\n\n(.*?)(?:--|$)", raw_email, re.DOTALL)
    if not plain_text_match:
        raise HTTPException(status_code=400, detail="Unable to extract plain text content from email")
    plain_text_content = plain_text_match.group(1).strip()

    # Check for unsubscribe keywords
    unsubscribe_detected = any(keyword in plain_text_content.lower() for keyword in UNSUBSCRIBE_KEYWORDS)

    # Return the response
    response = UnsubscribeResponse(email=sender_email, unsubscribe=unsubscribe_detected)
    return JSONResponse(content=response.dict())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)