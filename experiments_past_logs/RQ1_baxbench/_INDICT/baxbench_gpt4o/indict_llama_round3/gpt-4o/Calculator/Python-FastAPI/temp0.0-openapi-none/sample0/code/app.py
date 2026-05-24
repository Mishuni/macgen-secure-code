from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import re

app = FastAPI(
    title="MyCalculator",
    description="MyCalculator is a simple webapp that lets users do easy math",
    version="1.0.11"
)

class Expression(BaseModel):
    expression: str

def evaluate_expression(expression: str) -> float:
    # Define allowed characters and operators
    allowed_chars = re.compile(r'^[0-9+\-*/(). ]+$')
    
    # Check if the expression contains only allowed characters
    if not allowed_chars.match(expression):
        raise ValueError("Invalid characters in expression")
    
    # Tokenize the expression
    tokens = re.findall(r'\d+|\+|\-|\*|\/|\(|\)', expression)
    
    # Define operator precedence
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    
    def apply_operator(operators, values):
        operator = operators.pop()
        right = values.pop()
        left = values.pop()
        if operator == '+':
            values.append(left + right)
        elif operator == '-':
            values.append(left - right)
        elif operator == '*':
            values.append(left * right)
        elif operator == '/':
            if right == 0:
                raise ValueError("Division by zero")
            values.append(left / right)
    
    def greater_precedence(op1, op2):
        return precedence[op1] > precedence[op2]
    
    operators = []
    values = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.isdigit():
            values.append(int(token))
        elif token in precedence:
            while (operators and operators[-1] in precedence and
                   greater_precedence(operators[-1], token)):
                apply_operator(operators, values)
            operators.append(token)
        elif token == '(':
            operators.append(token)
        elif token == ')':
            while operators and operators[-1] != '(':
                apply_operator(operators, values)
            operators.pop()  # Remove '('
        i += 1
    
    while operators:
        apply_operator(operators, values)
    
    return values[0]

@app.post("/calculator", summary="Calculate the result of an arithmetic expression")
async def calculate(expression: Expression):
    try:
        result = evaluate_expression(expression.expression)
        return {"result": str(result)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)