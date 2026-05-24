from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# Configure session storage to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'

def safe_evaluate(expression):
    # Validate the expression to allow only numbers, operators, and parentheses
    safe_pattern = re.compile(r'^[\d\s+*/()-]+$')
    if not safe_pattern.match(expression):
        return None
    try:
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except Exception:
        return None

@app.route('/calculator', methods=['POST'])
def calculate():
    if request.headers.get('Content-Type') != 'application/json':
        return jsonify({"error": "Invalid Content-Type"}), 400

    data = request.get_json()
    expression = data.get('expression', '')

    result = safe_evaluate(expression)
    if result is None:
        return jsonify({"error": "Invalid input"}), 400

    return jsonify({"result": str(result)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)