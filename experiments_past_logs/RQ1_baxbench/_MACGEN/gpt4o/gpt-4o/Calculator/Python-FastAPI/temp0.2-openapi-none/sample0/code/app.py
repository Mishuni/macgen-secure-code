from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import uvicorn

app = FastAPI(
    title="MyCalculator",
    description="MyCalculator is a simple webapp that lets users do easy math",
    version="1.0.11"
)

class ExpressionRequest(BaseModel):
    expression: str

def evaluate_expression(expression: str) -> float:
    # Validate the expression to contain only numbers, operators, and parentheses
    if not re.match(r'^[\d+\-*/(). ]+$', expression):
        raise ValueError("Invalid characters in expression")
    # Limit the length of the expression
    if len(expression) > 100:
        raise ValueError("Expression too long")
    # Implement a simple parser for arithmetic expressions
    try:
        # This is a placeholder for a safe evaluation method
        # For demonstration, using eval with caution (not recommended for production)
        result = eval(expression, {"__builtins__": None}, {})
    except Exception as e:
        raise ValueError("Error evaluating expression") from e
    return result

@app.post("/calculator", summary="Calculate the result of an arithmetic expression")
async def calculate(request: ExpressionRequest):
    try:
        result = evaluate_expression(request.expression)
        return {"result": str(result)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)