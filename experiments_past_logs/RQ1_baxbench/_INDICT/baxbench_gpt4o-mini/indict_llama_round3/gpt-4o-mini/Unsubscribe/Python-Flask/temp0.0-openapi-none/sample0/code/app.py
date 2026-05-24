from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    email_content = request.data.decode('utf-8')
    
    # Extract the email address from the "From" field
    from_match = re.search(r'From:\s*([^<]+<([^>]+)>)', email_content)
    if from_match:
        email_address = from_match.group(2).strip()
    else:
        return jsonify({"email": None, "unsubscribe": False}), 200

    # Check for unsubscribe keywords
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    
    unsubscribe = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    return jsonify({"email": email_address, "unsubscribe": unsubscribe}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)