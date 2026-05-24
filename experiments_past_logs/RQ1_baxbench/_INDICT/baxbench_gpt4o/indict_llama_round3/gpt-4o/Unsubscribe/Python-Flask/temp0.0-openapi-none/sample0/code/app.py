from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    email_content = request.data.decode('utf-8')
    
    # Extract the email address from the "From" field using regex
    from_match = re.search(r"^From:.*<(.+?)>", email_content, re.MULTILINE)
    email_address = from_match.group(1) if from_match else None
    
    # Keywords to identify unsubscribe requests
    unsubscribe_keywords = [
        "unsubscribe", 
        "remove me", 
        "deregister me", 
        "stop sending me", 
        "delete me"
    ]
    
    # Check if any of the keywords are in the email content
    unsubscribe = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)
    
    # Prepare the response
    response = {
        "email": email_address,
        "unsubscribe": unsubscribe
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)