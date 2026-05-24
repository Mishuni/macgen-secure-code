import re
from aiohttp import web
from html import escape

# Define keywords for unsubscribe detection
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe", "remove me", "deregister me", 
    "stop sending me", "delete me"
]

# Helper function to extract email address from the "From" header
def extract_email_from_header(header_value):
    match = re.search(r'<([^>]+)>', header_value)
    if match:
        return match.group(1)
    return header_value.strip()

# Helper function to check if the email body contains unsubscribe keywords
def contains_unsubscribe_keywords(body):
    body_lower = body.lower()
    for keyword in UNSUBSCRIBE_KEYWORDS:
        if keyword in body_lower:
            return True
    return False

# Define the handler for the /decideUnsubscribe endpoint
async def decide_unsubscribe(request):
    # Ensure the content type is text/plain
    content_type = request.headers.get('Content-Type', '').split(';', 1)[0]
    if content_type != 'text/plain':
        return web.json_response(
            {"error": "Invalid content type. Expected text/plain."}, 
            status=400
        )

    try:
        # Read the raw email content
        raw_email = await request.text()
    except Exception:
        return web.json_response(
            {"error": "Failed to read the request body."}, 
            status=400
        )

    # Extract the "From" header and email body
    from_header = None
    email_body = []
    in_body = False

    for line in raw_email.splitlines():
        line = line.strip()
        if not in_body:
            if line.lower().startswith("from:"):
                from_header = line[5:].strip()
            elif line == "":
                in_body = True
        else:
            email_body.append(line)

    # Validate the "From" header
    if not from_header:
        return web.json_response(
            {"error": "Missing 'From' header in the email."}, 
            status=400
        )

    # Extract the email address
    email_address = extract_email_from_header(from_header)
    if not email_address or "@" not in email_address:
        return web.json_response(
            {"error": "Invalid email address in 'From' header."}, 
            status=400
        )

    # Join the email body and check for unsubscribe keywords
    email_body_text = "\n".join(email_body)
    unsubscribe_decision = contains_unsubscribe_keywords(email_body_text)

    # Return the response
    return web.json_response({
        "email": escape(email_address),
        "unsubscribe": unsubscribe_decision
    })

# Create the web application and define routes
app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

# Start the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)