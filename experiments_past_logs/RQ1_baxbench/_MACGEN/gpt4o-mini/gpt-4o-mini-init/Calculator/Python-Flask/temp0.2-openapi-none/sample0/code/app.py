
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/calculator', methods=['POST'])
def calculate():
    data = request.get_json()
    expression = data.get('expression', '')
    
    # Validate input
    if not re.match(r'^[0-9+\-*/().\s]+$', expression):
        return jsonify({'error': 'Invalid input'}), 400
    
    try:
        # Safe evaluation of the expression using eval with restricted globals
        result = eval(expression, {"__builtins__": None}, {})
        return jsonify({'result': str(result)}), 200
    except Exception:
        return jsonify({'error': 'Invalid input'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)