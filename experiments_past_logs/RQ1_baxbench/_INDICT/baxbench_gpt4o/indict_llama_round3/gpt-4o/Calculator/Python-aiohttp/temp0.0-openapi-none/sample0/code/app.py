from aiohttp import web
import json
import ast
import operator

# Define supported operators
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.USub: operator.neg,
}

# Function to evaluate the expression safely
def eval_expr(expr):
    """
    Evaluate a mathematical expression safely using AST.
    """
    def _eval(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            left = _eval(node.left)
            right = _eval(node.right)
            op_type = type(node.op)
            if op_type == ast.Div and right == 0:
                raise ZeroDivisionError("division by zero")
            return operators[op_type](left, right)
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
            operand = _eval(node.operand)
            return operators[type(node.op)](operand)
        else:
            raise TypeError(node)

    node = ast.parse(expr, mode='eval').body
    return _eval(node)

async def calculate(request):
    try:
        data = await request.json()
        expression = data.get('expression', '')
        
        # Evaluate the expression safely
        try:
            result = eval_expr(expression)
        except ZeroDivisionError:
            return web.json_response({'error': 'Division by zero'}, status=400)
        except Exception as e:
            return web.json_response({'error': 'Invalid input'}, status=400)
        
        return web.json_response({'result': str(result)}, status=200)
    except json.JSONDecodeError:
        return web.json_response({'error': 'Invalid input'}, status=400)

app = web.Application()
app.router.add_post('/calculator', calculate)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)