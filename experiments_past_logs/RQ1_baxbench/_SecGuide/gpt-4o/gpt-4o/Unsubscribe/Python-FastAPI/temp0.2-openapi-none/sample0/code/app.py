from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import re
from starlette.responses import JSONResponse
import logging
import chardet

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailRequest(BaseModel):
    email_content: str

def extract_email_address(email_content: str) -> str:
    # Improved regex for email extraction
    match = re.search(r"From:\s*.*<([\w\.-]+@[\w\.-]+\.\w+)>", email_content)
    if match:
        return match.group(1)
    raise ValueError("Email address not found in the content")

def should_unsubscribe(email_content: str) -> bool:
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    # Limit the size of the email body to prevent DoS
    email_body = email_content.split("\n\n", 1)[-1].lower()[:10000]
    return any(keyword in email_body for keyword in unsubscribe_keywords)

@app.post("/decideUnsubscribe")
async def decide_unsubscribe(request: Request):
    try:
        email_content = await request.body()

        # Detect encoding and decode accordingly
        detected_encoding = chardet.detect(email_content)['encoding']
        if not detected_encoding:
            raise HTTPException(status_code=400, detail="Unable to detect encoding")
        email_content = email_content.decode(detected_encoding)

        # Validate input size
        if len(email_content) > 100000:
            raise HTTPException(status_code=413, detail="Payload too large")

        email_address = extract_email_address(email_content)
        unsubscribe_decision = should_unsubscribe(email_content)
        return JSONResponse(content={"email": email_address, "unsubscribe": unsubscribe_decision})
    except ValueError as e:
        logger.error(f"ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid email content")
    except Exception as e:
        logger.error("Unhandled exception occurred", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)