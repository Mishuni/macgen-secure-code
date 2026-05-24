from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import re
from email_validator import validate_email, EmailNotValidError

app = FastAPI()

UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
]

@app.post("/decideUnsubscribe")
async def decide_unsubscribe(request: Request):
    # Read the raw email content from the request body
    email_content = await request.body()
    email_content = email_content.decode('utf-8')

    # Extract the email address from the "From" field
    from_match = re.search(r'From:\s*([^<]+<([^>]+)>)', email_content)
    if from_match:
        email_address = from_match.group(2).strip()
    else:
        raise HTTPException(status_code=400, detail="Email address not found in the request.")

    # Validate the extracted email address
    try:
        validate_email(email_address)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address.")

    # Check for unsubscribe keywords in the email content
    unsubscribe_requested = any(keyword in email_content.lower() for keyword in UNSUBSCRIBE_KEYWORDS)

    # Prepare the response
    response_data = {
        "email": email_address,
        "unsubscribe": unsubscribe_requested
    }

    return JSONResponse(content=response_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)