from aiohttp import web
import re
import json

# Define the keywords that indicate an unsubscribe request
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
]

# Function to check if the email content contains unsubscribe keywords
def should_unsubscribe(email_content):
    # Normalize the content to lower case for case-insensitive matching
    content_lower = email_content.lower()
    return any(keyword in content_lower for keyword in UNSUBSCRIBE_KEYWORDS)

# Endpoint to decide whether to unsubscribe
async def decide_unsubscribe(request):
    try:
        # Get the raw email content from the request body
        email_content = await request.text()
        
        # Extract the email address from the "From" field
        from_match = re.search(r'From:\s*([^<>\s]+<([^<>]+)>)|From:\s*([^<>\s]+)', email_content)
        if from_match:
            email_address = from_match.group(2) or from_match.group(3)
        else:
            return web.json_response({"error": "Email address not found"}, status=400)

        # Check if the email content indicates an unsubscribe request
        unsubscribe = should_unsubscribe(email_content)

        # Prepare the response
        response_data = {
            "email": email_address,
            "unsubscribe": unsubscribe
        }
        return web.json_response(response_data)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

# Create the application and add the route
app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

# Run the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)