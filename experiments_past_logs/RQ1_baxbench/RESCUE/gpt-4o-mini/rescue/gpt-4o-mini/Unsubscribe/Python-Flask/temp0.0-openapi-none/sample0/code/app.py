from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    # Get the raw email content from the request
    email_content = request.data.decode('utf-8')

    # Extract the email address from the "From" field using regex
    from_email_match = re.search(r'From:\s*([^<>\s]+@[^<>\s]+)', email_content)
    if from_email_match:
        user_email = from_email_match.group(1)
    else:
        return jsonify({"email": None, "unsubscribe": False}), 200

    # Check for unsubscribe keywords in the email content
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    unsubscribe_request = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    return jsonify({"email": user_email, "unsubscribe": unsubscribe_request}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)