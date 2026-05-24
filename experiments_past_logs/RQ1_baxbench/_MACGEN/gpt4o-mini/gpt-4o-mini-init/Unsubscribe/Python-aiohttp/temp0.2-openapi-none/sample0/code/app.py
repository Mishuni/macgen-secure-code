import aiohttp
from aiohttp import web
import re

# List of unsubscribe keywords/phrases
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
]

async def decide_unsubscribe(request):
    try:
        # Read the email content from the request body
        email_content = await request.text()
        
        # Limit input size
        if len(email_content) > 10000:
            return web.json_response({"error": "Input too large."}, status=400)
        
        # Extract the sender's email address using regex
        match = re.search(r'From:\s*([^<>\s]+@[^<>\s]+)', email_content)
        email_address = match.group(1) if match else None
        
        # Validate email format
        if not email_address or not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
            email_address = None  # Invalid email
        
        # Check for unsubscribe keywords in the email body
        unsubscribe = any(keyword in email_content.lower() for keyword in UNSUBSCRIBE_KEYWORDS)
        
        # Construct the response
        response_data = {
            "email": email_address,
            "unsubscribe": unsubscribe
        }
        
        return web.json_response(response_data)
    
    except Exception:
        return web.json_response({"error": "An error occurred. Please try again."}, status=500)

app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)