from aiohttp import web
import re

async def decide_unsubscribe(request):
    # Limit the size of the incoming request body
    MAX_REQUEST_SIZE = 1024 * 1024  # 1 MB
    if request.content_length is not None and request.content_length > MAX_REQUEST_SIZE:
        return web.json_response({"error": "Request body too large"}, status=413)

    # Get the raw email content from the request body
    email_content = await request.text()

    # Define keywords that indicate an unsubscribe request
    unsubscribe_keywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ]

    # Check if any of the keywords are present in the email content
    unsubscribe = any(re.search(r'\b' + re.escape(keyword) + r'\b', email_content, re.IGNORECASE) for keyword in unsubscribe_keywords)

    # Extract the email address from the "From" field in the email content
    from_match = re.search(r'From:\s*([^<>\s]+@[^<>\s]+)', email_content)
    email = from_match.group(1) if from_match else None

    # Validate the extracted email address using a more robust regex
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        email = None  # Invalidate malformed email

    # Prepare the response without exposing sensitive information
    response_data = {
        "unsubscribe": unsubscribe
    }

    if email:
        response_data["email"] = email  # Include email only if valid

    return web.json_response(response_data)

app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)