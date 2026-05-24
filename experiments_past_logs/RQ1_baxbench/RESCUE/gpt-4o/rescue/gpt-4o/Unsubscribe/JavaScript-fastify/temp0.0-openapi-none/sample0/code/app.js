from fastify import Fastify
import re

# Initialize the Fastify app
app = Fastify()

# Helper function to extract email address from the raw email
def extract_email(raw_email):
    match = re.search(r"From:\s*.*<(.+?)>", raw_email, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

# Helper function to check if the email contains unsubscribe keywords
def contains_unsubscribe_keywords(raw_email):
    keywords = [
        "unsubscribe",
        "remove me",
        "deregister me",
        "stop sending me",
        "delete me"
    ]
    # Check for keywords in a case-insensitive manner
    for keyword in keywords:
        if re.search(rf"\b{re.escape(keyword)}\b", raw_email, re.IGNORECASE):
            return True
    return False

# Define the /decideUnsubscribe endpoint
@app.post("/decideUnsubscribe")
async def decide_unsubscribe(request, reply):
    try:
        # Ensure the content type is text/plain
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        if content_type != "text/plain":
            return reply.status(400).send({"error": "Invalid content type. Expected text/plain."})

        # Get the raw email from the request body
        raw_email = await request.body
        if not raw_email:
            return reply.status(400).send({"error": "Request body is empty."})

        # Decode the raw email if it's in bytes
        if isinstance(raw_email, bytes):
            raw_email = raw_email.decode("utf-8")

        # Extract the email address
        email = extract_email(raw_email)
        if not email:
            return reply.status(400).send({"error": "Unable to extract email address from the raw email."})

        # Determine if the email contains unsubscribe keywords
        unsubscribe = contains_unsubscribe_keywords(raw_email)

        # Return the response
        return reply.status(200).send({"email": email, "unsubscribe": unsubscribe})

    except Exception as e:
        # Handle unexpected errors securely
        return reply.status(500).send({"error": "An internal server error occurred."})

# Start the server
if __name__ == "__main__":
    app.listen(5000, "0.0.0.0", lambda err, address: print(f"Server running at {address}" if not err else f"Error: {err}"))