from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import re

app = FastAPI()

class CalculationRequest(BaseModel):
    expression: str

class CalculationResponse(BaseModel):
    result: str

def evaluate_expression(expression: str) -> str:
    # Validate the expression to ensure it only contains safe characters
    if not re.match(r'^[\d\s+\-*/()]+$', expression):
        raise ValueError("Invalid input: expression contains unsafe characters")
    
    try:
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, {})
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {str(e)}")
    
    return str(result)

@app.post("/calculator", response_model=CalculationResponse)
async def calculate(request: CalculationRequest):
    try:
        result = evaluate_expression(request.expression)
        return CalculationResponse(result=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)