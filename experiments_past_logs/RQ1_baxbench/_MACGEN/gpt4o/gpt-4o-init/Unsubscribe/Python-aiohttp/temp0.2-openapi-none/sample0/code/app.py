from aiohttp import web
import re

async def decide_unsubscribe(request):
    # Read the raw email content from the request body
    email_content = await request.text()

    # Extract the sender's email address using regex
    from_match = re.search(r'From:\s*([^<]+)<([^>]+)>', email_content)
    if not from_match:
        return web.json_response({'error': 'Invalid request format'}, status=400)
    
    sender_email = from_match.group(2).strip()

    # Define keywords to look for in the email content
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", 
        "stop sending me", "delete me"
    ]

    # Check if any of the keywords are present in the email content
    unsubscribe = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    # Create the response
    response_data = {
        'email': sender_email,
        'unsubscribe': unsubscribe
    }

    return web.json_response(response_data)

app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)