from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import operator
import re

app = FastAPI()

class ExpressionRequest(BaseModel):
    expression: str

@app.post("/calculator")
async def calculate(request: ExpressionRequest):
    try:
        # Validate and evaluate the expression
        result = eval_expression(request.expression)
        return {"result": str(result)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid input")

def eval_expression(expr: str):
    # Validate the expression using regex
    if not re.match(r'^[\d\s\+\-\*/\(\)]+$', expr):
        raise ValueError("Expression contains invalid characters")
    
    # Evaluate the expression safely
    try:
        # Replace operators with functions
        tokens = re.findall(r'\d+|[+\-*/()]', expr)
        return evaluate_tokens(tokens)
    except ZeroDivisionError:
        raise ValueError("Division by zero is not allowed")
    except Exception:
        raise ValueError("Error evaluating the expression")

def evaluate_tokens(tokens):
    def apply_operator(operators, values):
        operator = operators.pop()
        right = values.pop()
        left = values.pop()
        values.append(operators_map[operator](left, right))

    def precedence(op):
        if op in ('+', '-'):
            return 1
        if op in ('*', '/'):
            return 2
        return 0

    operators = []
    values = []
    for token in tokens:
        if token.isdigit():
            values.append(int(token))
        elif token in operators_map:
            while (operators and precedence(operators[-1]) >= precedence(token)):
                apply_operator(operators, values)
            operators.append(token)
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            operators.pop()  # Remove '('

    while operators:
        apply_operator(operators, values)

    return values[0]

operators_map = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)