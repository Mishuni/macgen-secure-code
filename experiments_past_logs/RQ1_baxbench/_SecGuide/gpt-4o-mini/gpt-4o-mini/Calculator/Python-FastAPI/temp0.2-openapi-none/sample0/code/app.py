from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
import re
import sympy as sp

app = FastAPI()

class ExpressionRequest(BaseModel):
    # Restrict the expression to a maximum length and valid characters
    expression: constr(regex=r'^[0-9+\-*/().\s]{1,100}$')  # Limit to 100 characters

@app.post("/calculator")
async def calculate(request: ExpressionRequest):
    # Validate the expression to prevent code injection
    if not re.match(r'^[0-9+\-*/().\s]+$', request.expression):
        raise HTTPException(status_code=400, detail="Invalid input")

    try:
        # Parse and evaluate the expression safely using sympy
        expr = sp.sympify(request.expression)
        result = expr.evalf()
        return {"result": str(result)}
    except (sp.SympifyError, ValueError, ZeroDivisionError) as e:
        raise HTTPException(status_code=400, detail="Invalid input or mathematical error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)