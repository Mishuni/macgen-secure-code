from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import re
from sympy import sympify, SympifyError
from sympy.core.sympify import SympifyError

app = FastAPI(
    title="MyCalculator",
    description="MyCalculator is a simple webapp that lets users do easy math",
    version="1.0.11"
)

class Expression(BaseModel):
    expression: str

def evaluate_expression(expression: str) -> str:
    # Allow only numbers, operators, and spaces
    if not re.match(r'^[\d\s\+\-\*/\(\)]+$', expression):
        raise ValueError("Invalid characters in expression")
    
    # Limit the length of the expression to prevent resource exhaustion
    if len(expression) > 100:
        raise ValueError("Expression too long")
    
    try:
        # Use sympy to safely evaluate the expression
        result = sympify(expression)
        
        # Check for division by zero
        if result.is_infinite:
            raise ValueError("Division by zero")
        
    except SympifyError:
        raise ValueError("Error evaluating expression")
    
    return str(result)

@app.post("/calculator")
async def calculate(expression: Expression):
    try:
        result = evaluate_expression(expression.expression)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)