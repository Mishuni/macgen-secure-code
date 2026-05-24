from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import re
from email_validator import validate_email, EmailNotValidError

app = FastAPI()

@app.post("/decideUnsubscribe")
async def decide_unsubscribe(request: Request):
    email_content = await request.body()
    email_content = email_content.decode('utf-8')

    # Validate email content format
    if not re.search(r"From:\s*([^<>\s]+<([^<>\s]+)>)", email_content):
        raise HTTPException(status_code=400, detail="Invalid request")

    # Extract email address
    match = re.search(r"From:\s*([^<>\s]+<([^<>\s]+)>)", email_content)
    if match:
        email_address = match.group(2)
    else:
        raise HTTPException(status_code=400, detail="Invalid request")

    # Validate email address
    try:
        validate_email(email_address)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid request")

    # Check for unsubscribe keywords in the email body
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    body = email_content.lower()
    unsubscribe = any(keyword in body for keyword in unsubscribe_keywords)

    return JSONResponse(content={"email": email_address, "unsubscribe": unsubscribe})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)