from flask import Flask, request, jsonify, make_response
from html import escape
import re

app = Flask(__name__)

# Keywords to identify unsubscribe requests
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe", 
    "remove me", 
    "deregister me", 
    "stop sending me", 
    "delete me"
]

# Helper function to extract email address from the "From" header
def extract_email(from_header):
    # Regex to match email addresses
    email_regex = r'<([^>]+)>'
    match = re.search(email_regex, from_header)
    if match:
        return match.group(1)
    return None

# Helper function to check if the email body contains unsubscribe keywords
def contains_unsubscribe_keywords(email_body):
    email_body_lower = email_body.lower()
    for keyword in UNSUBSCRIBE_KEYWORDS:
        if keyword in email_body_lower:
            return True
    return False

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    # Ensure the Content-Type is text/plain
    if request.content_type != 'text/plain':
        return make_response(jsonify({"error": "Invalid Content-Type. Expected text/plain"}), 400)

    try:
        # Read the raw email content
        raw_email = request.data.decode('utf-8')
    except Exception:
        return make_response(jsonify({"error": "Invalid email content"}), 400)

    # Extract the "From" header
    from_header_match = re.search(r'^From:(.+)$', raw_email, re.MULTILINE)
    if not from_header_match:
        return make_response(jsonify({"error": "Missing or invalid 'From' header"}), 400)
    
    from_header = from_header_match.group(1).strip()
    email_address = extract_email(from_header)
    if not email_address:
        return make_response(jsonify({"error": "Unable to extract email address from 'From' header"}), 400)

    # Extract the email body
    body_match = re.search(r'\r?\n\r?\n(.+)', raw_email, re.DOTALL)
    if not body_match:
        return make_response(jsonify({"error": "Unable to extract email body"}), 400)
    
    email_body = body_match.group(1).strip()

    # Check if the email body contains unsubscribe keywords
    unsubscribe = contains_unsubscribe_keywords(email_body)

    # Return the decision
    response = {
        "email": escape(email_address),  # Escape the email address to prevent XSS
        "unsubscribe": unsubscribe
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)