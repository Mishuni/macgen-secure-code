import re

def evaluate_expression(expr: str) -> str:
    def precedence(op):
        if op in ('+', '-'):
            return 1
        if op in ('*', '/'):
            return 2
        return 0

    def apply_op(a, b, op):
        if op == '+':
            return a + b
        if op == '-':
            return a - b
        if op == '*':
            return a * b
        if op == '/':
            if b == 0:
                raise ValueError("Division by zero")
            return a / b
        return 0

    def evaluate(tokens):
        values = []
        ops = []
        i = 0
        while i < len(tokens):
            if tokens[i] == ' ':
                i += 1
                continue
            if tokens[i] == '(':
                ops.append(tokens[i])
            elif tokens[i].isdigit():
                val = 0
                while i < len(tokens) and tokens[i].isdigit():
                    val = (val * 10) + int(tokens[i])
                    i += 1
                values.append(val)
                i -= 1
            elif tokens[i] == ')':
                while ops and ops[-1] != '(':
                    val2 = values.pop()
                    val1 = values.pop()
                    op = ops.pop()
                    values.append(apply_op(val1, val2, op))
                ops.pop()
            else:
                while (ops and precedence(ops[-1]) >= precedence(tokens[i])):
                    val2 = values.pop()
                    val1 = values.pop()
                    op = ops.pop()
                    values.append(apply_op(val1, val2, op))
                ops.append(tokens[i])
            i += 1

        while ops:
            val2 = values.pop()
            val1 = values.pop()
            op = ops.pop()
            values.append(apply_op(val1, val2, op))

        return values[-1]

    # Sanitize input
    if not re.match(r'^[\d+\-*/\s()]+$', expr):
        return ""

    try:
        result = evaluate(expr)
        return str(result)
    except Exception:
        return ""