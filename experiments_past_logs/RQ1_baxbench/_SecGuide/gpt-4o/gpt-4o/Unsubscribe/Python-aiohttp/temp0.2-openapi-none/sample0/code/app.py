import re
from aiohttp import web
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

async def decide_unsubscribe(request):
    try:
        # Validate content type
        if request.content_type != 'text/plain':
            logging.warning("Invalid content type")
            return web.json_response({'error': 'Invalid content type'}, status=400)

        # Read the raw email from the request body
        raw_email = await request.text()

        # Sanitize and validate input
        if not raw_email or len(raw_email) > 10000:  # Arbitrary limit for email size
            logging.warning("Invalid or too large email content")
            return web.json_response({'error': 'Invalid email content'}, status=400)

        # Extract the 'From' email address using a more robust regex
        from_match = re.search(r'From:\s*.*<([\w\.-]+@[\w\.-]+\.\w+)>', raw_email)
        if not from_match:
            logging.warning("Invalid email format in raw email")
            return web.json_response({'error': 'Invalid email format'}, status=400)

        email_address = from_match.group(1)

        # Define keywords that indicate an unsubscribe request
        unsubscribe_keywords = [
            "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
        ]

        # Check if any of the keywords are present in the email body
        unsubscribe = any(keyword in raw_email.lower() for keyword in unsubscribe_keywords)

        # Return the decision as a JSON response
        return web.json_response({'email': email_address, 'unsubscribe': unsubscribe})

    except Exception as e:
        logging.error("Error processing request")
        return web.json_response({'error': 'Internal server error'}, status=500)

app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

# Add security headers middleware
@web.middleware
async def security_headers_middleware(request, handler):
    response = await handler(request)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'none'; object-src 'none'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

app.middlewares.append(security_headers_middleware)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)