from flask import Flask, request, jsonify, make_response
from email import message_from_bytes
from email.policy import default
import secrets
from flask_wtf.csrf import CSRFProtect
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
csrf = CSRFProtect(app)

# Keywords indicating unsubscribe request
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
]

def contains_unsubscribe_keywords(email_body):
    """Check if the email body contains any unsubscribe keywords."""
    email_body_lower = email_body.lower()
    return any(keyword in email_body_lower for keyword in UNSUBSCRIBE_KEYWORDS)

@app.route('/decideUnsubscribe', methods=['POST'])
@csrf.exempt  # CSRF protection is not needed for API endpoints, but ensure it's used where necessary
def decide_unsubscribe():
    # Validate content type
    if request.content_type not in ['application/json', 'application/x-www-form-urlencoded']:
        return make_response(jsonify({"error": "Invalid content type"}), 400)

    # Get raw email from request body
    raw_email = request.data

    # Parse the email using the email library
    try:
        email_message = message_from_bytes(raw_email, policy=default)
    except Exception as e:
        return make_response(jsonify({"error": "Failed to parse email"}), 400)

    # Extract email address from the 'From' header
    email_address = email_message.get('From')
    if not email_address:
        return make_response(jsonify({"error": "Invalid email format"}), 400)

    # Extract the plain text part of the email
    plain_text_body = None
    if email_message.is_multipart():
        for part in email_message.iter_parts():
            if part.get_content_type() == 'text/plain':
                plain_text_body = part.get_payload(decode=True).decode(part.get_content_charset())
                break
    else:
        if email_message.get_content_type() == 'text/plain':
            plain_text_body = email_message.get_payload(decode=True).decode(email_message.get_content_charset())

    if not plain_text_body:
        return make_response(jsonify({"error": "Plain text part not found"}), 400)

    # Determine if the email contains unsubscribe keywords
    unsubscribe = contains_unsubscribe_keywords(plain_text_body)

    # Generate a pseudorandom value for CSRF protection
    csrf_token = secrets.token_urlsafe(16)
    response = make_response(jsonify({"unsubscribe": unsubscribe}))
    response.set_cookie('csrf_token', csrf_token, httponly=True, secure=True)

    return response

@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')