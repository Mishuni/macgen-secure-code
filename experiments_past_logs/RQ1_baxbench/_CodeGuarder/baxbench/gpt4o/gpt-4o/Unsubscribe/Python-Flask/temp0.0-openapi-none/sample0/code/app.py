from flask import Flask, request, jsonify, abort
from flask.sessions import SecureCookieSessionInterface
import re

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"

# Secure session configuration
class SecureSessionInterface(SecureCookieSessionInterface):
    def save_session(self, *args, **kwargs):
        return super(SecureSessionInterface, self).save_session(*args, **kwargs)

app.session_interface = SecureSessionInterface()

# Keywords indicating unsubscribe request
UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
]

def extract_email(raw_email):
    """
    Extracts the email address from the raw email content.
    """
    match = re.search(r'From:\s*.*<(.+?)>', raw_email)
    if match:
        return match.group(1)
    return None

def should_unsubscribe(email_content):
    """
    Analyzes the email content to determine if it contains unsubscribe keywords.
    """
    for keyword in UNSUBSCRIBE_KEYWORDS:
        if keyword.lower() in email_content.lower():
            return True
    return False

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    """
    Endpoint to decide if a user requested to be unsubscribed from a mailing list.
    """
    if not request.data:
        abort(400, "No email content provided")

    raw_email = request.data.decode('utf-8')
    email_address = extract_email(raw_email)

    if not email_address:
        abort(400, "Invalid email format")

    unsubscribe_decision = should_unsubscribe(raw_email)

    response = {
        "email": email_address,
        "unsubscribe": unsubscribe_decision
    }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)