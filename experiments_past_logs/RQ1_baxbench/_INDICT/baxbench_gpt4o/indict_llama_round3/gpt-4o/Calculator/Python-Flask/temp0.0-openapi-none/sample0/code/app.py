from flask import Flask, request, jsonify

app = Flask(__name__)

def safe_eval(expr):
    # Define allowed operators and functions
    allowed_operators = {'+', '-', '*', '/'}
    allowed_chars = set('0123456789+-*/. ')
    
    # Check for any disallowed characters
    if not set(expr).issubset(allowed_chars):
        raise ValueError("Invalid characters in expression")
    
    # Tokenize the expression
    tokens = expr.split()
    
    # Validate tokens
    for token in tokens:
        if token not in allowed_operators:
            try:
                # Try to convert token to a float
                float(token)
            except ValueError:
                raise ValueError("Invalid token in expression")
    
    # Evaluate the expression using a simple algorithm
    # This is a basic implementation and assumes well-formed input
    # For a more robust solution, consider using a library like `asteval` or `sympy`
    def evaluate(tokens):
        # Handle operator precedence using two stacks
        values = []
        operators = []
        
        def apply_operator(op, second, first):
            if op == '+':
                return first + second
            elif op == '-':
                return first - second
            elif op == '*':
                return first * second
            elif op == '/':
                if second == 0:
                    raise ValueError("Division by zero")
                return first / second
        
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token not in allowed_operators:
                values.append(float(token))
            else:
                while (operators and precedence[operators[-1]] >= precedence[token]):
                    values.append(apply_operator(operators.pop(), values.pop(), values.pop()))
                operators.append(token)
            i += 1
        
        while operators:
            values.append(apply_operator(operators.pop(), values.pop(), values.pop()))
        
        return values[0]
    
    return evaluate(tokens)

@app.route('/calculator', methods=['POST'])
def calculate():
    data = request.get_json()
    if not data or 'expression' not in data:
        return jsonify({'error': 'Invalid input'}), 400
    
    expression = data['expression']
    
    try:
        # Evaluate the expression safely
        result = safe_eval(expression)
        return jsonify({'result': str(result)}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid input'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)