from aiohttp import web
import re

async def decide_unsubscribe(request):
    # Get the raw email content from the request
    email_content = await request.text()
    
    # Check for empty email content
    if not email_content.strip():
        return web.json_response({"email": None, "unsubscribe": False}, status=400)

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
    from_match = re.search(r'From:\s*([^<]*<([^>]+)>)|From:\s*([^<]+)', email_content)
    email_address = from_match.group(2) if from_match and from_match.group(2) else (from_match.group(3) if from_match and from_match.group(3) else None)
    
    # Prepare the response
    response_data = {
        "email": email_address,
        "unsubscribe": unsubscribe
    }
    
    return web.json_response(response_data)

app = web.Application()
app.router.add_post('/decideUnsubscribe', decide_unsubscribe)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)