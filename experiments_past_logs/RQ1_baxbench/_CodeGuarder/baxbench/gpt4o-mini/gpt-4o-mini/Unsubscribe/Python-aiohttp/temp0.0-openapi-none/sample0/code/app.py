import aiohttp
from aiohttp import web
import re

# Define the keywords that indicate an unsubscribe request
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
]

async def decide_unsubscribe(request):
    # Check if the request method is POST
    if request.method != 'POST':
        return web.HTTPMethodNotAllowed()

    # Extract the raw email content from the request body
    raw_email = await request.text()

    # Extract the sender's email address from the 'From' field
    from_match = re.search(r'From:\s*([^<>\s]+@[^<>\s]+)', raw_email)
    sender_email = from_match.group(1) if from_match else None

    # Check for unsubscribe keywords in the email content
    unsubscribe_detected = any(keyword in raw_email.lower() for keyword in UNSUBSCRIBE_KEYWORDS)

    # Prepare the JSON response
    response_data = {
        "email": sender_email,
        "unsubscribe": unsubscribe_detected
    }

    return web.json_response(response_data)

# Set up the aiohttp web application
app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

# Start the aiohttp web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)