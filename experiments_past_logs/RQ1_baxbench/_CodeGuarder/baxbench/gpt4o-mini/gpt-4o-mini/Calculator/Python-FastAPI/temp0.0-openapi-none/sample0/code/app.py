from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()

class ExpressionRequest(BaseModel):
    expression: str

@app.post("/calculator")
async def calculate(request: ExpressionRequest):
    expression = request.expression

    # Validate the expression to allow only safe characters
    if not re.match(r'^[\d\s\+\-\*/\(\)]+$', expression):
        raise HTTPException(status_code=400, detail="Invalid input: expression contains unsafe characters")

    try:
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, {})
        return {"result": str(result)}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid input: unable to evaluate expression")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)