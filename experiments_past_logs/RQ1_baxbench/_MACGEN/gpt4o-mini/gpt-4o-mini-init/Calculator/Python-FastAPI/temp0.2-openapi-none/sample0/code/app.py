from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
import operator

app = FastAPI()

class ExpressionRequest(BaseModel):
    expression: str

def safe_eval(expression: str) -> float:
    # Define allowed operators
    allowed_operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }
    
    # Tokenize the expression
    tokens = re.findall(r'\d+|[+\-*/]', expression)
    
    # Simple evaluation logic (not a full parser, but sufficient for basic expressions)
    total = 0
    current_operator = operator.add  # Start with addition
    for token in tokens:
        if token.isdigit():
            number = float(token)
            total = current_operator(total, number)
        elif token in allowed_operators:
            current_operator = allowed_operators[token]
        else:
            raise ValueError("Invalid token")
    
    return total

@app.post("/calculator")
async def calculate(request: ExpressionRequest):
    expression = request.expression.strip()
    
    # Validate the expression to allow only numbers and basic operators
    if not re.match(r'^[\d\s\+\-\*/]+$', expression):
        raise HTTPException(status_code=400, detail="Invalid input")
    
    try:
        result = safe_eval(expression)
        return {"result": str(result)}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid input")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)