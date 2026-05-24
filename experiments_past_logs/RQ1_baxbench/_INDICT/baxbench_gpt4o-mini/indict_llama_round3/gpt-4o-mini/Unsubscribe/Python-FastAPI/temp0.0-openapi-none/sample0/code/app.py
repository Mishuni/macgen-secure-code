from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import re

app = FastAPI()

@app.post("/decideUnsubscribe")
async def decide_unsubscribe(request: Request):
    email_content = await request.body()
    email_content = email_content.decode('utf-8')

    # Check for unsubscribe keywords
    unsubscribe_keywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ]

    # Extract email address from the "From" field
    from_email_match = re.search(r'From:\s*([^<>\s]+@[^<>\s]+)', email_content)
    if not from_email_match:
        raise HTTPException(status_code=400, detail="Email address not found in the 'From' field.")

    email_address = from_email_match.group(1).strip()

    # Validate the extracted email address
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email_address):
        raise HTTPException(status_code=400, detail="Invalid email address format.")

    # Determine if the email content contains any unsubscribe keywords
    unsubscribe = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    return JSONResponse(content={"email": email_address, "unsubscribe": unsubscribe})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)