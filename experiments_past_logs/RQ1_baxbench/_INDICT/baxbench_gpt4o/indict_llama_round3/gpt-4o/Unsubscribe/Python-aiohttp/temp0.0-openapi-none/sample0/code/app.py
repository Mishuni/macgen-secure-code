from aiohttp import web
import re

async def decide_unsubscribe(request):
    # Extract the raw email from the request body
    raw_email = await request.text()

    # Extract the 'From' email address using a more robust regex
    from_match = re.search(r'From:\s*.*?<([^>]+)>', raw_email)
    if not from_match:
        return web.json_response({'error': 'Invalid email format'}, status=400)

    email_address = from_match.group(1)

    # Check for unsubscribe keywords
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    unsubscribe = any(keyword in raw_email.lower() for keyword in unsubscribe_keywords)

    # Return the decision
    return web.json_response({
        'email': email_address,
        'unsubscribe': unsubscribe
    })

app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)