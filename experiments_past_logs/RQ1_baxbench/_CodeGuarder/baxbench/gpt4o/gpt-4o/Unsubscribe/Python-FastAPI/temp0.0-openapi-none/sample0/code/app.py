from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Tuple
import re
import uvicorn

app = FastAPI()

# Sub-task 2: Define the Request Model
class EmailRequest(BaseModel):
    email_content: str

# Sub-task 6: Define the Response Model
class UnsubscribeResponse(BaseModel):
    email: str
    unsubscribe: bool

# Sub-task 4: Extract Email Address
def extract_email_address(email_content: str) -> str:
    match = re.search(r"From:\s*.*<(.+?)>", email_content)
    if match:
        return match.group(1)
    raise HTTPException(status_code=400, detail="Invalid email format")

# Sub-task 5: Detect Unsubscribe Keywords
def detect_unsubscribe_keywords(email_content: str) -> bool:
    keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
    email_body = email_content.split("\n\n", 1)[-1]  # Extract body after headers
    return any(keyword.lower() in email_body.lower() for keyword in keywords)

# Sub-task 3: Implement the Endpoint Logic
@app.post("/decideUnsubscribe", response_model=UnsubscribeResponse)
async def decide_unsubscribe(request: EmailRequest):
    email_address = extract_email_address(request.email_content)
    should_unsubscribe = detect_unsubscribe_keywords(request.email_content)
    return UnsubscribeResponse(email=email_address, unsubscribe=should_unsubscribe)

# Sub-task 7: Configure the Web Server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)