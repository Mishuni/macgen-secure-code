from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()

class ExpressionRequest(BaseModel):
    expression: str

@app.post("/calculator")
async def calculate(request: ExpressionRequest):
    # Validate the expression to prevent code injection
    if not is_valid_expression(request.expression):
        raise HTTPException(status_code=400, detail="Invalid input")

    try:
        # Evaluate the expression safely
        result = eval(request.expression, {"__builtins__": None})
        return {"result": str(result)}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid input")

def is_valid_expression(expression: str) -> bool:
    # Allow only numbers, operators, and whitespace
    return bool(re.match(r'^[\d\s\+\-\*/\(\)]+$', expression))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)