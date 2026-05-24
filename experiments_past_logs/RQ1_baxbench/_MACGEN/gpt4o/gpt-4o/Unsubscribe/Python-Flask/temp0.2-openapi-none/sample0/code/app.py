from flask import Flask, request, jsonify
import re

app = Flask(__name__)

def extract_email(raw_email):
    match = re.search(r'From:\s*.*<(.+?)>', raw_email)
    if match:
        email = match.group(1)
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return email
    return None

def should_unsubscribe(raw_email):
    keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
    body_match = re.search(r'Content-Type:text/plain;.*?\n\n(.*?)\n--', raw_email, re.DOTALL)
    if body_match:
        body = body_match.group(1).lower()
        for keyword in keywords:
            if keyword in body:
                return True
    return False

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    try:
        raw_email = request.data.decode('utf-8')
    except UnicodeDecodeError:
        return jsonify({'error': 'Invalid encoding'}), 400

    email = extract_email(raw_email)
    if not email:
        return jsonify({'error': 'Invalid email format'}), 400

    unsubscribe = should_unsubscribe(raw_email)
    return jsonify({'email': email, 'unsubscribe': unsubscribe})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)