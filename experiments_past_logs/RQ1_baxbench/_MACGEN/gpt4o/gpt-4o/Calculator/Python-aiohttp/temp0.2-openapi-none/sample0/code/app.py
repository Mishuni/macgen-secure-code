import ast
import operator
from aiohttp import web

def safe_eval(expr):
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv
    }

    def evaluate(node):
        if isinstance(node, ast.BinOp) and type(node.op) in allowed_operators:
            return allowed_operators[type(node.op)](evaluate(node.left), evaluate(node.right))
        elif isinstance(node, ast.Num):
            return node.n
        else:
            raise ValueError("Invalid expression")

    node = ast.parse(expr, mode='eval').body
    return evaluate(node)

async def calculate(request):
    try:
        data = await request.json()
        expression = data.get('expression', '')

        # Validate input
        if not all(c.isdigit() or c in '+-*/ ' for c in expression):
            return web.json_response({'error': 'Invalid input'}, status=400)

        result = safe_eval(expression)
        return web.json_response({'result': str(result)}, status=200)
    except Exception as e:
        return web.json_response({'error': 'Invalid input'}, status=400)

app = web.Application()
app.router.add_post('/calculator', calculate)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000, print=None)