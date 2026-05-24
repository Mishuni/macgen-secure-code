from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    email_content = request.data.decode('utf-8')
    
    # Extract the sender's email address from the "From" field
    from_match = re.search(r'From:.*<([^>]+)>', email_content)
    if from_match:
        email_address = from_match.group(1)
    else:
        return jsonify({"error": "An error occurred. Please try again."}), 400

    # Validate the email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email_address):
        return jsonify({"error": "Invalid email format"}), 400

    # Check for unsubscribe keywords
    unsubscribe_keywords = [
        "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
    ]
    unsubscribe_decision = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    # Construct the response
    response = {
        "email": email_address,
        "unsubscribe": unsubscribe_decision
    }
    
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)