from flask import Flask, request, jsonify, abort
import re

app = Flask(__name__)
app.config['SESSION_TYPE'] = "filesystem"  # Secure session storage configuration

UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
]

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    if request.content_type != 'text/plain':
        abort(400, description="Invalid content type. Expected text/plain.")

    raw_email_content = request.data.decode('utf-8')
    from_email = extract_from_email(raw_email_content)

    if from_email and contains_unsubscribe_keywords(raw_email_content):
        response = {
            "email": from_email,
            "unsubscribe": True
        }
    else:
        response = {
            "email": from_email,
            "unsubscribe": False
        }

    return jsonify(response), 200

def extract_from_email(raw_email_content):
    match = re.search(r'From:\s*(.*?)(?:\r\n|\n)', raw_email_content)
    return match.group(1).strip() if match else None

def contains_unsubscribe_keywords(content):
    return any(keyword in content.lower() for keyword in UNSUBSCRIBE_KEYWORDS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)