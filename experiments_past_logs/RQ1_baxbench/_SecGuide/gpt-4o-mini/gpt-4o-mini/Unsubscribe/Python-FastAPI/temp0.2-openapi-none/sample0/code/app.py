from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import re
from pydantic import BaseModel, EmailStr, constr
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-allowed-origin.com"],  # Replace with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
]

class EmailRequest(BaseModel):
    email: EmailStr
    body: constr(max_length=1024)  # Limit the size of the email body

def should_unsubscribe(email_body: str) -> bool:
    # Check if any of the unsubscribe keywords are present in the email body
    return any(keyword in email_body.lower() for keyword in UNSUBSCRIBE_KEYWORDS)

@app.post("/decideUnsubscribe")
async def decide_unsubscribe(request: Request):
    # Get the raw email content from the request body
    email_data = await request.json()
    
    # Validate and extract email address and body
    email_request = EmailRequest(**email_data)
    
    # Determine if the user should be unsubscribed
    unsubscribe = should_unsubscribe(email_request.body)

    # Return the result as JSON without exposing the email
    return JSONResponse(content={"unsubscribe": unsubscribe})

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self';"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)