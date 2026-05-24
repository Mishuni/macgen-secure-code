from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ValidationError
from typing import Dict
import uvicorn
import ast

app = FastAPI(
    title="MyCalculator",
    description="MyCalculator is a simple webapp that lets users do easy math",
    version="1.0.11"
)

class ExpressionRequest(BaseModel):
    expression: str

@app.post("/calculator", summary="Calculate the result of an arithmetic expression")
async def calculate_expression(request: ExpressionRequest):
    try:
        # Parse the expression safely using ast.literal_eval
        expression = request.expression
        # Validate that the expression only contains safe nodes
        allowed_nodes = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.USub, ast.Load)
        parsed_expr = ast.parse(expression, mode='eval')
        for node in ast.walk(parsed_expr):
            if not isinstance(node, allowed_nodes):
                raise ValueError("Invalid expression")
        # Evaluate the expression
        result = eval(compile(parsed_expr, filename="<string>", mode="eval"))
        return {"result": str(result)}
    except (SyntaxError, ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)