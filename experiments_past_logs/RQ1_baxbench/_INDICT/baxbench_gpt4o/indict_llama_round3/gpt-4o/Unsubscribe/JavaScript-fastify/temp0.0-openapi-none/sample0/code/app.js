from fastify import Fastify

app = Fastify()

def extract_email(raw_email):
    """Extracts the email address from the raw email content."""
    for line in raw_email.splitlines():
        if line.startswith("From:"):
            start = line.find("<") + 1
            end = line.find(">")
            if start > 0 and end > start:
                return line[start:end]
    return None

def should_unsubscribe(raw_email):
    """Determines if the email contains unsubscribe keywords."""
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    lower_email = raw_email.lower()
    for keyword in unsubscribe_keywords:
        if keyword in lower_email:
            return True
    return False

@app.post('/decideUnsubscribe')
async def decide_unsubscribe(request, reply):
    raw_email = await request.body()
    email = extract_email(raw_email)
    unsubscribe = should_unsubscribe(raw_email)
    return reply.send({
        "email": email,
        "unsubscribe": unsubscribe
    })

if __name__ == '__main__':
    app.listen(5000, '0.0.0.0')