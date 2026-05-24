from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/decideUnsubscribe', methods=['POST'])
def decide_unsubscribe():
    # Get the raw email content from the request
    email_content = request.data.decode('utf-8')

    # Check for unsubscribe keywords
    unsubscribe_keywords = [
        "unsubscribe", 
        "remove me", 
        "deregister me", 
        "stop sending me", 
        "delete me"
    ]
    
    # Check if any of the keywords are in the email content
    unsubscribe = any(keyword in email_content.lower() for keyword in unsubscribe_keywords)

    # Extract the email address from the "From" header
    from_header = next((line for line in email_content.splitlines() if line.startswith("From:")), None)
    email_address = None
    
    if from_header:
        # Use regex to extract the email address safely
        match = re.search(r'<([^>]+)>', from_header)
        if match:
            email_address = match.group(1).strip()
            # Validate the extracted email address with a more robust regex
            if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email_address):
                email_address = None

    # Return the response without exposing sensitive information
    response = {
        "unsubscribe": unsubscribe
    }
    
    # Only include the email address if it was successfully validated
    if email_address:
        response["email"] = email_address

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)