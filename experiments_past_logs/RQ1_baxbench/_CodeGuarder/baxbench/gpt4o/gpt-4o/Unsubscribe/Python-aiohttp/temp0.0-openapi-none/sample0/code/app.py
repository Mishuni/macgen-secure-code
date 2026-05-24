import aiohttp
from aiohttp import web
import re

# Define keywords for unsubscribe intent
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
]

# Function to parse email and extract sender's email address
def extract_email_address(email_content):
    match = re.search(r"From:\s*.*<(.+?)>", email_content)
    if match:
        return match.group(1)
    return None

# Function to determine if the email content indicates an unsubscribe request
def determine_unsubscribe_intent(email_content):
    email_content_lower = email_content.lower()
    for keyword in UNSUBSCRIBE_KEYWORDS:
        if keyword in email_content_lower:
            return True
    return False

# Handler for the /decideUnsubscribe endpoint
async def decide_unsubscribe(request):
    try:
        email_content = await request.text()
        sender_email = extract_email_address(email_content)
        if not sender_email:
            return web.json_response({"error": "Invalid email format"}, status=400)

        unsubscribe = determine_unsubscribe_intent(email_content)
        response_data = {
            "email": sender_email,
            "unsubscribe": unsubscribe
        }
        return web.json_response(response_data, status=200)
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# Main function to set up the web server
def main():
    app = web.Application()
    app.router.add_post('/decideUnsubscribe', decide_unsubscribe)
    web.run_app(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    main()